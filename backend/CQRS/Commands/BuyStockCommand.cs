namespace backend.CQRS.Commands
{
    public class BuyStockCommand
    {
        public string UserId { get; set; }
        public string Symbol { get; set; }
        public int Shares { get; set; }
        public decimal Price { get; set; }
    }
}
