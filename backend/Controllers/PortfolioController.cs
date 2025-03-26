using backend.CQRS.Commands;
using backend.CQRS.Queries;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using System.Threading.Tasks;
using backend.Services;
using backend.Models;
using backend.Data;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PortfolioController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public PortfolioController(ApplicationDbContext context)
        {
            _context = context;
        }

        [HttpGet("{userId}")]
        public async Task<IActionResult> GetPortfolio(Guid userId)
        {
            var portfolio = await _context.Portfolios
                .Include(p => p.Stocks)
                .Include(p => p.Transactions)
                .FirstOrDefaultAsync(p => p.UserId == userId);

            if (portfolio == null)
                return NotFound(new { error = "Portfolio not found" });

            return Ok(portfolio);
        }
    }


}

