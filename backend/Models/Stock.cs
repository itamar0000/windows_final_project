using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace backend.Models
{
    public class Stock
    {
        [Key]
        public int Id { get; set; } // Unique ID for each stock entry

        [Required]
        [MaxLength(10)]
        public string Symbol { get; set; } // Stock symbol (e.g., "AAPL")

        [Required]
        public int Shares { get; set; } // Number of shares owned

        [Required]
        public decimal CurrentPrice { get; set; } // Price per share

        [NotMapped] // This property is calculated dynamically, not stored in DB
        public decimal TotalValue => Shares * CurrentPrice; // Total value of shares

        // Foreign key linking stock to a portfolio
        public int PortfolioId { get; set; }
        public Portfolio Portfolio { get; set; } // Navigation property
    }
}
