using System.Net.Http;
using System.Net.Http.Json;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using backend.Models;
using backend.Data;
using backend.CQRS.Queries;
using System.Net.Http.Json;
using System.Text.Json;


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
        private readonly string _apiKeyfinn;
        private readonly string _apiKeyTwelve;

        private readonly ApplicationDbContext _context;


        public StockService(IConfiguration config)
        {
            _http = new HttpClient();
            _apiKeyfinn = config["Finnhub:ApiKey"];
            _apiKeyTwelve = config["TwelveData:ApiKey"];

        }
        public async Task<decimal?> HandleQuery(GetStockPriceQuery query)
        {
            return await GetCurrentPrice(query.Symbol); // Assuming GetCurrentPrice already exists
        }

        public async Task<decimal?> GetCurrentPrice(string symbol)
        {
            var url = $"https://finnhub.io/api/v1/quote?symbol={symbol}&token={_apiKeyfinn}";
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

        public async Task<List<StockHistoryPoint>> GetStockHistory(GetStockHistoryQuery query)
        {

            var toDate = DateTime.UtcNow;
            var fromDate = toDate.AddYears(-10); // Always get 5 years of data


            var fromStr = fromDate.ToString("yyyy-MM-dd");
            var toStr = toDate.ToString("yyyy-MM-dd");
            var url = $"https://api.twelvedata.com/time_series?symbol={query.Symbol}&interval=1day&start_date={fromStr}&end_date={toStr}&apikey={_apiKeyTwelve}";

            Console.WriteLine($" URL: {url}");

            var response = await _http.GetAsync(url);
            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($" HTTP ERROR: {response.StatusCode}");
                return new List<StockHistoryPoint>();
            }

            var jsonString = await response.Content.ReadAsStringAsync();

            using var jsonDoc = JsonDocument.Parse(jsonString);
            if (!jsonDoc.RootElement.TryGetProperty("values", out var values))
                return new List<StockHistoryPoint>();

            var result = new List<StockHistoryPoint>();
            foreach (var item in values.EnumerateArray())
            {
                if (item.TryGetProperty("datetime", out var dateProp) &&
                    item.TryGetProperty("close", out var closeProp) &&
                    DateTime.TryParse(dateProp.GetString(), out var date) &&
                    decimal.TryParse(closeProp.GetString(), out var close))
                {
                    result.Add(new StockHistoryPoint
                    {
                        Date = date,
                        Price = close
                    });
                }
            }

            return result.OrderBy(p => p.Date).ToList();
        }





    }
}
