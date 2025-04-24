using Microsoft.AspNetCore.Mvc;
using backend.Services;


namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AiAdvisorController : ControllerBase
    {
        private readonly AiAdvisorService _aiAdvisorService;

        public AiAdvisorController(AiAdvisorService aiAdvisorService)
        {
            _aiAdvisorService = aiAdvisorService;
        }

        [HttpPost("ask")]
        public async Task<IActionResult> Ask([FromBody] AiQuestionRequest request)
        {
            var answer = await _aiAdvisorService.AskQuestionAsync(request.Question);
            return Ok(new { response = answer });
        }
    }

    public class AiQuestionRequest
    {
        public string Question { get; set; }
    }
}
