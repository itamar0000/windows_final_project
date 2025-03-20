using System.ComponentModel.DataAnnotations;

namespace backend.Models
{
    public class User
    {
        [Key]
        public int Id { get; set; }

        [Required]
        [MaxLength(50)]
        public string Username { get; set; }

        [Required]
        public string PasswordHash { get; set; }  // Hashed password for security

        public string? Email { get; set; }  // Optional email field

        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}
