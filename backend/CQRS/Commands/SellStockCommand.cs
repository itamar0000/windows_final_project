namespace backend.CQRS.Commands
{
    public class SellStockCommand
    {
        public string UserId { get; set; }
        public string Symbol { get; set; }
        public int Shares { get; set; }
    }
}
