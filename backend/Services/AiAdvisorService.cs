using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace backend.Services
{
    public class AiAdvisorService
    {
        private readonly HttpClient _http;

        public AiAdvisorService(HttpClient? httpClient = null)
        {
            _http = httpClient ?? new HttpClient();
        }

        public async Task<string> AskQuestionAsync(string question)
        {
            var requestBody = new
            {
                model = "gemma:2b",
                prompt = question,
                stream = false
            };

            var content = new StringContent(
                JsonSerializer.Serialize(requestBody),
                Encoding.UTF8,
                "application/json"
            );

            try
            {
                var response = await _http.PostAsync("http://localhost:11434/api/generate", content);
                var responseText = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    return "Error talking to AI model.";
                }

                var json = JsonDocument.Parse(responseText);
                if (json.RootElement.TryGetProperty("response", out var result))
                    return result.GetString() ?? "No response from model.";

                return "Unexpected response format.";
            }
            catch (Exception ex)
            {
                Console.WriteLine("AI ERROR: " + ex.Message);
                return "AI is currently unavailable. Please try again later.";
            }
        }
    }
}
