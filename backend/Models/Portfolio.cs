namespace backend.Models
{
    public class Portfolio
    {
        public Guid Id { get; set; }

        public Guid UserId { get; set; }
        public User User { get; set; }

        public ICollection<Stock> Stocks { get; set; } 
        public ICollection<Transaction> Transactions { get; set; }
    }
}
