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
                .Include(p => p.User)
                .Include(p => p.Transactions)  // 👈 This was missing

                .FirstOrDefaultAsync(p => p.UserId == userId);

            if (portfolio == null)
                return NotFound(new { error = "Portfolio not found" });

            // Get transactions for this user
            var transactions = await _context.Transactions
                .Where(t => t.UserId == userId)
                .OrderByDescending(t => t.Timestamp)
                .ToListAsync();

            return Ok(new
            {
                portfolio.Id,
                portfolio.UserId,
                User = new
                {
                    portfolio.User.Id,
                    portfolio.User.Username,
                    portfolio.User.ProfileImageUrl
                },
                Stocks = portfolio.Stocks.Select(s => new
                {
                    s.Symbol,
                    s.Shares,
                    s.CurrentPrice
                }),
                Transactions = transactions.Select(t => new
                {
                    t.Symbol,
                    t.Shares,
                    t.Price,
                    t.ActionType,
                    t.Timestamp
                })
            });
        }


    }


}

