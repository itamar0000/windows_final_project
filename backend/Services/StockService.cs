using System.Net.Http;
using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using backend.Models;
using backend.Data;
using backend.CQRS.Queries;

namespace backend.Services
{
    public class StockHistoryPoint
    {
        public DateTime Date { get; set; }
        public decimal Price { get; set; }
    }

    public class FinnhubCandleResponse
    {
        [System.Text.Json.Serialization.JsonPropertyName("c")]
        public List<decimal> ClosePrices { get; set; }

        [System.Text.Json.Serialization.JsonPropertyName("t")]
        public List<long> Timestamps { get; set; }

        [System.Text.Json.Serialization.JsonPropertyName("s")]
        public string Status { get; set; }
    }

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
        public async Task<decimal?> HandleQuery(GetStockPriceQuery query)
        {
            return await GetCurrentPrice(query.Symbol); // Assuming GetCurrentPrice already exists
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

        public async Task<List<StockHistoryPoint>> HandleQuery(GetStockHistoryQuery query)
        {

            var to = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            long from;
            string resolution;

            switch (query.Range.ToLower())
            {
                case "day":
                    from = DateTimeOffset.UtcNow.AddDays(-1).ToUnixTimeSeconds();
                    resolution = "5";
                    break;
                case "week":
                    from = DateTimeOffset.UtcNow.AddDays(-7).ToUnixTimeSeconds();
                    resolution = "30";
                    break;
                case "month":
                    from = DateTimeOffset.UtcNow.AddMonths(-1).ToUnixTimeSeconds();
                    resolution = "D";
                    break;
                case "year":
                    from = DateTimeOffset.UtcNow.AddYears(-1).ToUnixTimeSeconds();
                    resolution = "W";
                    break;
                case "10years":
                    from = DateTimeOffset.UtcNow.AddYears(-10).ToUnixTimeSeconds();
                    resolution = "M";
                    break;
                default:
                    throw new ArgumentException("Invalid range");
            }

            var url = $"https://finnhub.io/api/v1/stock/candle?symbol={query.Symbol}&resolution={resolution}&from={from}&to={to}&token={_apiKey}";
            var response = await _http.GetAsync(url);


            if (!response.IsSuccessStatusCode)
                return new List<StockHistoryPoint>();

            var data = await response.Content.ReadFromJsonAsync<FinnhubCandleResponse>();

            Console.WriteLine($"DEBUG: Finnhub candle URL => {url}");

            if (data != null)
                Console.WriteLine($"DEBUG: Status = {data.Status}, Points = {data.Timestamps?.Count}");
            else
                Console.WriteLine("DEBUG: Response was null");

            if (data?.Status != "ok" || data.Timestamps == null)
                return new List<StockHistoryPoint>();

            var result = new List<StockHistoryPoint>();
            for (int i = 0; i < data.Timestamps.Count; i++)
            {
                result.Add(new StockHistoryPoint
                {
                    Date = DateTimeOffset.FromUnixTimeSeconds(data.Timestamps[i]).DateTime,
                    Price = data.ClosePrices[i]
                });
            }

            return result;
        }



    }
}
