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
        private readonly StockService _stockService;


        public PortfolioService(ApplicationDbContext dbContext, StockService stockService)
        {
            _dbContext = dbContext;
            _stockService = stockService;
        }


        public async Task<bool> HandleCommand(BuyStockCommand command)
        {
            var user = await _dbContext.Users.FindAsync(command.UserId);
            if (user == null) return false;

            var price = await _stockService.GetCurrentPrice(command.Symbol);
            if (price == null) return false;

            var stock = new Stock
            {
                Symbol = command.Symbol,
                Shares = command.Shares,
                CurrentPrice = price.Value
            };


            var portfolio = await _dbContext.Portfolios
                .Include(p => p.Stocks)
               .Include(p => p.Transactions)  // 👈 This was missing

                .FirstOrDefaultAsync(p => p.UserId == command.UserId);
            if (portfolio == null)
            {
                portfolio = new Portfolio { UserId = command.UserId, Stocks = new List<Stock>() };
                _dbContext.Portfolios.Add(portfolio);
            }

            var existingStock = portfolio.Stocks.FirstOrDefault(s => s.Symbol == command.Symbol);

            if (existingStock != null)
            {
                existingStock.Shares += command.Shares;
                existingStock.CurrentPrice = price.Value;
            }
            else
            {
                var newStock = new Stock
                {
                    Symbol = command.Symbol,
                    Shares = command.Shares,
                    CurrentPrice = price.Value,
                    PortfolioId = portfolio.Id
                };
                portfolio.Stocks.Add(newStock);
            }
            await _dbContext.SaveChangesAsync();
            return true;
        }

        public async Task<bool> HandleCommand(SellStockCommand command)
        {
            var portfolio = await _dbContext.Portfolios
                .Include(p => p.Stocks)
                        .Include(p => p.Transactions)  // 👈 This was missing

                .FirstOrDefaultAsync(p => p.UserId == command.UserId);
            if (portfolio == null)
                return false;

            if (portfolio.Stocks == null)
                return false;

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
                .Include(p => p.Transactions)  // 👈 This was missing

                .FirstOrDefaultAsync(p => p.UserId == query.UserId);
        }
    }
}
