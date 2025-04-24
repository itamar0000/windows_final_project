//using System.Text.Json;
//using System.Text;

//public class AiAdvisorService
//{
//    private readonly HttpClient _httpClient;
//    private readonly ILogger<AiAdvisorService> _logger;

//    public AiAdvisorService(HttpClient httpClient, ILogger<AiAdvisorService> logger)
//    {
//        _httpClient = httpClient;
//        _httpClient.Timeout = TimeSpan.FromMinutes(2); // Increase timeout
//        _logger = logger;
//    }

//    public async Task<string> AskQuestionAsync(string question)
//    {
//        try
//        {
//            // This matches Ollama's actual API format
//            var request = new
//            {
//                model = "gemma:2b",
//                prompt = question,
//                stream = false // Set to false to get a complete response
//            };

//            _logger.LogInformation("Sending request to Ollama API: {request}", JsonSerializer.Serialize(request));

//            var content = new StringContent(
//                JsonSerializer.Serialize(request),
//                Encoding.UTF8,
//                "application/json");

//            var response = await _httpClient.PostAsync("http://localhost:11434/api/generate", content);
//            response.EnsureSuccessStatusCode();

//            var responseBody = await response.Content.ReadAsStringAsync();
//            _logger.LogInformation("Received response: {response}", responseBody);

//            // Parse the actual Ollama response format
//            using var jsonDoc = JsonDocument.Parse(responseBody);
//            return jsonDoc.RootElement.GetProperty("response").GetString() ??
//                   "No response content received from AI service.";
//        }
//        catch (Exception ex)
//        {
//            _logger.LogError(ex, "Error communicating with Ollama API");
//            return "AI service error: " + ex.Message;
//        }
//    }
//}
using System.Text.Json;
using System.Text;
using System.Collections.Generic;

public class AiAdvisorService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AiAdvisorService> _logger;
    private readonly IVectorStore _vectorStore; // Interface for your vector store

    public AiAdvisorService(HttpClient httpClient, ILogger<AiAdvisorService> logger, IVectorStore vectorStore)
    {
        _httpClient = httpClient;
        _httpClient.Timeout = TimeSpan.FromMinutes(2); // Increase timeout
        _logger = logger;
        _vectorStore = vectorStore;
    }

    public async Task<string> AskQuestionAsync(string question, int topK = 3)
    {
        try
        {
            // Step 1: Retrieve relevant context using the question
            var relevantDocs = await _vectorStore.SearchAsync(question, topK);

            // Step 2: Format context into a string
            string context = FormatContextFromDocs(relevantDocs);

            // Step 3: Construct prompt with context and question
            string prompt = $@"I have the following information:

{context}

Based on this information, please answer the question: {question}";

            _logger.LogInformation("Using RAG with {count} relevant documents", relevantDocs.Count);

            // Step 4: Send to Ollama with the enhanced prompt
            var request = new
            {
                model = "gemma:2b",
                prompt = prompt,
                stream = false
            };

            _logger.LogInformation("Sending request to Ollama API with RAG context");
            var content = new StringContent(
                JsonSerializer.Serialize(request),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync("http://localhost:11434/api/generate", content);
            response.EnsureSuccessStatusCode();
            var responseBody = await response.Content.ReadAsStringAsync();

            // Parse the actual Ollama response format
            using var jsonDoc = JsonDocument.Parse(responseBody);
            return jsonDoc.RootElement.GetProperty("response").GetString() ??
                   "No response content received from AI service.";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error communicating with Ollama API or vector store");
            return "AI service error: " + ex.Message;
        }
    }

    private string FormatContextFromDocs(List<Document> documents)
    {
        var sb = new StringBuilder();

        for (int i = 0; i < documents.Count; i++)
        {
            sb.AppendLine($"Document {i + 1}:");
            sb.AppendLine(documents[i].Content);
            sb.AppendLine();
        }

        return sb.ToString();
    }
}

// Interface for your vector store implementation
public interface IVectorStore
{
    Task<List<Document>> SearchAsync(string query, int topK = 3);
}

// Simple document model - adjust to match your actual implementation
public class Document
{
    public string Id { get; set; }
    public string Content { get; set; }
    public float[] Embedding { get; set; }
}

// Sample implementation - replace with your actual vector store implementation
public class YourVectorStore : IVectorStore
{
    // This is where you would implement your vector similarity search
    // using the embeddings you've already created
    public async Task<List<Document>> SearchAsync(string query, int topK = 3)
    {
        // 1. Generate embedding for the query
        // 2. Find most similar vectors to the query embedding
        // 3. Return the corresponding documents

        // This is just a placeholder - implement your actual vector search logic
        throw new NotImplementedException("Implement your vector search logic here");
    }
}