﻿using System.Text.Json;
using System.Text;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using Microsoft.Data.Sqlite;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System;

public class AiAdvisorService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AiAdvisorService> _logger;
    private readonly List<DocumentVector> _vectors = new();
    private readonly string _vectorFilePath;
    private const int DefaultEmbeddingDimension = 384; // Adjust if you change embedding model

    public AiAdvisorService(HttpClient httpClient, ILogger<AiAdvisorService> logger, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _httpClient.Timeout = TimeSpan.FromMinutes(2);
        _logger = logger;
        _vectorFilePath = configuration["VectorStorage:FilePath"] ?? "RAG/chroma.sqlite3";

        LoadVectors();
    }

    private void LoadVectors()
    {
        LoadVectorsFromChromaDb(_vectorFilePath);
    }

    private void LoadVectorsFromChromaDb(string sqlitePath)
    {
        try
        {
            if (!File.Exists(sqlitePath))
            {
                _logger.LogWarning("Chroma DB not found at {path}", sqlitePath);
                return;
            }

            string connectionString = $"Data Source={sqlitePath};Mode=ReadOnly;";
            using var connection = new SqliteConnection(connectionString);
            connection.Open();

            var command = connection.CreateCommand();
            command.CommandText = @"
                SELECT e.id, d.document, e.embedding
                FROM embedding e
                JOIN documents d ON e.document_id = d.id
            ";

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                string id = reader.GetString(0);
                string content = reader.GetString(1);
                byte[] blob = (byte[])reader["embedding"];
                float[] embedding = BytesToFloatArray(blob);

                _vectors.Add(new DocumentVector
                {
                    Id = id,
                    Content = content,
                    Embedding = embedding
                });
            }

            _logger.LogInformation("Loaded {count} document vectors from Chroma DB.", _vectors.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load vectors from {path}", sqlitePath);
        }
    }

    private float[] BytesToFloatArray(byte[] bytes)
    {
        if (bytes.Length % 4 != 0)
            throw new InvalidDataException("Invalid float array byte length");

        int count = bytes.Length / 4;
        float[] floats = new float[count];

        for (int i = 0; i < count; i++)
            floats[i] = BitConverter.ToSingle(bytes, i * 4);

        return floats;
    }

    public async Task<string> AskQuestionAsync(string question)
    {
        try
        {
            var relevantDocuments = FindRelevantDocuments(question, topK: 15);

            if (relevantDocuments.Count == 0)
            {
                _logger.LogWarning("No relevant documents found for the question: {question}", question);
            }

            string combinedContext = string.Join("\n\n", relevantDocuments.Select(doc => doc.Content));

            string prompt = $@"
You are a financial advisor AI.

Use the following CONTEXT to answer the QUESTION.

### CONTEXT:
{combinedContext}

### QUESTION:
{question}

### INSTRUCTIONS:
- Only answer based on the context provided.
- Be clear, structured, and professional in your answer.
- Start answering directly without repeating the question.

### ANSWER:
";

            _logger.LogInformation("Sending prompt to Ollama:\n{prompt}", prompt);

            var request = new
            {
                model = "gemma:2b",
                prompt = prompt,
                stream = false
            };

            var content = new StringContent(
                JsonSerializer.Serialize(request),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync("http://localhost:11434/api/generate", content);
            response.EnsureSuccessStatusCode();

            var responseBody = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Received response from Ollama.");

            using var jsonDoc = JsonDocument.Parse(responseBody);
            return jsonDoc.RootElement.GetProperty("response").GetString() ??
                   "No response content received from AI service.";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error communicating with Ollama API");
            return "AI service error: " + ex.Message;
        }
    }

    private List<DocumentVector> FindRelevantDocuments(string query, int topK)
    {
        if (_vectors.Count == 0)
            return new List<DocumentVector>();

        try
        {
            float[] queryEmbedding = GetQueryEmbedding(query);

            var similarities = _vectors.Select(doc => new
            {
                Document = doc,
                Score = CosineSimilarity(queryEmbedding, doc.Embedding)
            })
            .OrderByDescending(x => x.Score)
            .Take(topK)
            .ToList();

            _logger.LogInformation("Found {count} similar documents for the query.", similarities.Count);

            return similarities.Select(s => s.Document).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error finding relevant documents.");
            return new List<DocumentVector>();
        }
    }

    private float[] GetQueryEmbedding(string query)
    {
        // TODO: Replace this with actual embedding generation
        _logger.LogWarning("Using dummy query embedding. Replace with real embedding generation!");
        return new float[DefaultEmbeddingDimension];
    }

    private float CosineSimilarity(float[] vecA, float[] vecB)
    {
        if (vecA.Length != vecB.Length)
            throw new ArgumentException("Vectors must be of the same length");

        float dotProduct = 0;
        float magnitudeA = 0;
        float magnitudeB = 0;

        for (int i = 0; i < vecA.Length; i++)
        {
            dotProduct += vecA[i] * vecB[i];
            magnitudeA += vecA[i] * vecA[i];
            magnitudeB += vecB[i] * vecB[i];
        }

        magnitudeA = (float)Math.Sqrt(magnitudeA);
        magnitudeB = (float)Math.Sqrt(magnitudeB);

        return (magnitudeA == 0 || magnitudeB == 0) ? 0 : dotProduct / (magnitudeA * magnitudeB);
    }
}

public class DocumentVector
{
    public string Id { get; set; }
    public string Content { get; set; }
    public float[] Embedding { get; set; }
}
