namespace backend.CQRS.Commands
{
    public class SellStockCommand
    {
        public Guid UserId { get; set; }
        public string Symbol { get; set; }
        public int Shares { get; set; }
    }
}
