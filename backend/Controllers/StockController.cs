using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using backend.Services;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class StocksController : ControllerBase
    {
        private readonly StockService _stockService;

        public StocksController(StockService stockService)
        {
            _stockService = stockService;
        }

        [HttpGet("{symbol}/price")]
        public async Task<IActionResult> GetPrice(string symbol)
        {
            var price = await _stockService.GetCurrentPrice(symbol);
            if (price == null)
                return NotFound(new { error = "Stock not found or API error" });

            return Ok(new { symbol, price });
        }
    }
}
