﻿using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using backend.Services;
using backend.CQRS.Commands;
using backend.CQRS.Queries;


namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class StockController : ControllerBase
    {
        private readonly StockService _stockService;
        private readonly PortfolioService _portfolioService;

        public StockController(StockService stockService, PortfolioService portfolioService)
        {
            _stockService = stockService;
            _portfolioService = portfolioService;
        }

        [HttpGet("{symbol}/price")]
        public async Task<IActionResult> GetPrice(string symbol)
        {
            var query = new GetStockPriceQuery(symbol);
            var price = await _stockService.HandleQuery(query);

            if (price == null)
                return NotFound(new { error = "Stock not found or API error" });

            return Ok(new { symbol, price });
        }


        [HttpPost("buy")]
        public async Task<IActionResult> Buy([FromBody] BuyStockCommand command)
        {
            var success = await _stockService.ExecuteBuyOrder(command.UserId, command.Symbol, command.Shares); // ✅
            return success ? Ok(true) : BadRequest("Buy failed.");
        }


        [HttpPost("sell")]
        public async Task<IActionResult> Sell([FromBody] SellStockCommand command)
        {
            var success = await _stockService.ExecuteSellOrder(command.UserId, command.Symbol, command.Shares); // ✅
            return success ? Ok(true) : BadRequest("Sell failed.");
        }


        [HttpGet("{symbol}/history")]
        public async Task<IActionResult> GetStockHistory(string symbol)
        {
            var query = new GetStockHistoryQuery(symbol);
            var history = await _stockService.GetStockHistory(query);

            if (history == null || history.Count == 0)
                return NotFound(new { error = "No historical data found" });

            return Ok(history);
        }

    }
}
