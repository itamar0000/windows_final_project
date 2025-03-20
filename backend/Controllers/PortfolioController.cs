using backend.CQRS.Commands;
using backend.CQRS.Queries;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using System.Threading.Tasks;
using backend.Services;
using backend.Models;

namespace backend.Controllers
{
    [Route("api/portfolio")]
    [ApiController]
    [Authorize]
    public class PortfolioController : ControllerBase
    {
        private readonly PortfolioService _portfolioService;

        public PortfolioController(PortfolioService portfolioService)
        {
            _portfolioService = portfolioService;
        }


        [HttpGet]
        public async Task<IActionResult> GetPortfolio()
        {
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId == null) return Unauthorized();

            var query = new GetPortfolioQuery { UserId = userId };
            var portfolio = await _portfolioService.HandleQuery(query);

            if (portfolio == null) return NotFound("Portfolio not found");
            return Ok(portfolio);
        }

        [HttpPost("buy")]
        public async Task<IActionResult> BuyStock([FromBody] Transaction request)
        {
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId == null) return Unauthorized();

            var command = new BuyStockCommand { UserId = userId, Symbol = request.Symbol, Shares = request.Shares, Price = request.Price };
            var success = await _portfolioService.HandleCommand(command);

            if (!success) return BadRequest("Failed to buy stock");
            return Ok("Stock purchased successfully");
        }

        [HttpPost("sell")]
        public async Task<IActionResult> SellStock([FromBody] Transaction request)
        {
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId == null) return Unauthorized();

            var command = new SellStockCommand { UserId = userId, Symbol = request.Symbol, Shares = request.Shares };
            var success = await _portfolioService.HandleCommand(command);

            if (!success) return BadRequest("Failed to sell stock");
            return Ok("Stock sold successfully");
        }

    }

}

