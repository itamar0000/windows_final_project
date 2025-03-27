using System.Net.Http;
using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using backend.Models;
using backend.Data;

namespace backend.Services
{
    public class StockService
    {
        private readonly HttpClient _http;
        private readonly string _apiKey;
        private readonly ApplicationDbContext _context;


        public StockService(IConfiguration config)
        {
            _http = new HttpClient();
            _apiKey = config["Finnhub:ApiKey"];
        }
        public async Task<decimal?> GetCurrentPrice(string symbol)
        {
            var url = $"https://finnhub.io/api/v1/quote?symbol={symbol}&token={_apiKey}";
            var response = await _http.GetAsync(url);

            if (!response.IsSuccessStatusCode)
                return null;

            var json = await response.Content.ReadFromJsonAsync<FinnhubQuoteResponse>();
            return json?.c;
        }

        private class FinnhubQuoteResponse
        {
            public decimal c { get; set; } // current price
        }
        public async Task<bool> ExecuteBuyOrder(Guid userId, string symbol, int shares)
        {
            var price = await GetCurrentPrice(symbol);
            if (price == null)
                return false;

            var user = await _context.Users.FindAsync(userId);
            if (user == null)
                return false;

            // Get or create the user's portfolio
            var portfolio = await _context.Portfolios
                .Include(p => p.Stocks)
                .FirstOrDefaultAsync(p => p.UserId == userId);

            if (portfolio == null)
            {
                portfolio = new Portfolio { UserId = userId, Stocks = new List<Stock>() };
                _context.Portfolios.Add(portfolio);
            }

            // Update or add stock
            var stock = portfolio.Stocks.FirstOrDefault(s => s.Symbol == symbol);
            if (stock != null)
            {
                stock.Shares += shares;
                stock.CurrentPrice = price.Value;
            }
            else
            {
                stock = new Stock
                {
                    Symbol = symbol,
                    Shares = shares,
                    CurrentPrice = price.Value,
                    Portfolio = portfolio
                };
                portfolio.Stocks.Add(stock);
            }

            // Add transaction
            var transaction = new Transaction
            {
                Symbol = symbol,
                Shares = shares,
                Price = price.Value,
                ActionType = "Buy",
                Timestamp = DateTime.UtcNow,
                UserId = userId
            };
            _context.Transactions.Add(transaction);

            await _context.SaveChangesAsync();
            return true;
        }
        public async Task<bool> ExecuteSellOrder(Guid userId, string symbol, int shares)
        {
            var price = await GetCurrentPrice(symbol);
            if (price == null)
                return false;

            var portfolio = await _context.Portfolios
                .Include(p => p.Stocks)
                .FirstOrDefaultAsync(p => p.UserId == userId);

            if (portfolio == null)
                return false;

            var stock = portfolio.Stocks.FirstOrDefault(s => s.Symbol == symbol);
            if (stock == null || stock.Shares < shares)
                return false;

            stock.Shares -= shares;
            stock.CurrentPrice = price.Value;

            if (stock.Shares == 0)
                _context.Stocks.Remove(stock);

            // Add transaction
            var transaction = new Transaction
            {
                Symbol = symbol,
                Shares = shares,
                Price = price.Value,
                ActionType = "Sell",
                Timestamp = DateTime.UtcNow,
                UserId = userId
            };
            _context.Transactions.Add(transaction);

            await _context.SaveChangesAsync();
            return true;
        }


    }
}
