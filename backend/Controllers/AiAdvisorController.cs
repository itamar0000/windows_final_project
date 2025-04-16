using Microsoft.AspNetCore.Mvc;
using backend.Services;


namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AiAdvisorController : ControllerBase
    {
        private readonly AiAdvisorService _advisor;

        public AiAdvisorController(AiAdvisorService advisor)
        {
            _advisor = advisor;
        }

        [HttpPost("ask")]
        public async Task<IActionResult> AskQuestion([FromBody] AiQuestionRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Question))
                return BadRequest("Question cannot be empty.");

            var answer = await _advisor.AskQuestionAsync(request.Question);
            return Ok(new { response = answer });
        }
    }

    public class AiQuestionRequest
    {
        public string Question { get; set; } = string.Empty;
    }
}
