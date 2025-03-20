using backend.CQRS.Commands;
using backend.CQRS.Queries;
using backend.Models;
using backend.Data;
using Microsoft.EntityFrameworkCore;
using System.Threading.Tasks;

namespace backend.Services
{
    public class PortfolioService
    {
        private readonly ApplicationDbContext _dbContext;

        public PortfolioService(ApplicationDbContext dbContext)
        {
            _dbContext = dbContext;
        }

        public async Task<bool> HandleCommand(BuyStockCommand command)
        {
            var user = await _dbContext.Users.FindAsync(command.UserId);
            if (user == null) return false;

            var stock = new Stock
            {
                Symbol = command.Symbol,
                Shares = command.Shares,
                CurrentPrice = command.Price
            };

            var portfolio = await _dbContext.Portfolios.FirstOrDefaultAsync(p => p.UserId == command.UserId);
            if (portfolio == null)
            {
                portfolio = new Portfolio { UserId = command.UserId, Stocks = new List<Stock>() };
                _dbContext.Portfolios.Add(portfolio);
            }

            portfolio.Stocks.Add(stock);
            await _dbContext.SaveChangesAsync();
            return true;
        }

        public async Task<bool> HandleCommand(SellStockCommand command)
        {
            var portfolio = await _dbContext.Portfolios.FirstOrDefaultAsync(p => p.UserId == command.UserId);
            if (portfolio == null) return false;

            var stock = portfolio.Stocks.FirstOrDefault(s => s.Symbol == command.Symbol);
            if (stock == null || stock.Shares < command.Shares) return false;

            stock.Shares -= command.Shares;
            if (stock.Shares == 0) portfolio.Stocks.Remove(stock);

            await _dbContext.SaveChangesAsync();
            return true;
        }

        public async Task<Portfolio?> HandleQuery(GetPortfolioQuery query)
        {
            return await _dbContext.Portfolios
                .Include(p => p.Stocks)
                .FirstOrDefaultAsync(p => p.UserId == query.UserId);
        }
    }
}
