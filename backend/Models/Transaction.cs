namespace backend.Models
{
    public class Transaction
    {
        public Guid Id { get; set; }

        public string Symbol { get; set; }
        public int Shares { get; set; }
        public decimal Price { get; set; }
        public DateTime Timestamp { get; set; }
        public string ActionType { get; set; }  // "Buy" or "Sell"

        public Guid UserId { get; set; }
        public User User { get; set; }
    }
}
