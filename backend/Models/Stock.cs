namespace backend.Models
{
    public class Stock
    {
        public Guid Id { get; set; }
        public string Symbol { get; set; }
        public int Shares { get; set; }
        public decimal CurrentPrice { get; set; }

        public Guid PortfolioId { get; set; }
        public Portfolio Portfolio { get; set; }
    }
}
