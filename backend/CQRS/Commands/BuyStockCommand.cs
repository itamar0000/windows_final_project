namespace backend.CQRS.Commands
{
    public class BuyStockCommand
    {
        public Guid UserId { get; set; }
        public string Symbol { get; set; }
        public int Shares { get; set; }
    }

}
