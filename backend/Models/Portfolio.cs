using System.ComponentModel.DataAnnotations;
using System.Collections.Generic;

namespace backend.Models
{
    public class Portfolio
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public string UserId { get; set; } // User ID who owns this portfolio

        public List<Stock> Stocks { get; set; } = new List<Stock>(); // Stocks in portfolio
    }
}
