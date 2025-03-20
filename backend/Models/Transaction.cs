namespace backend.Models
{
    public class Transaction
    {
        public string Symbol { get; set; }
        public int Shares { get; set; }
        public decimal Price { get; set; }  // Optional for selling
    }
}