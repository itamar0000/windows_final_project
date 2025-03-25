using backend.Models;
using backend.Data;
using backend.Services;

using backend.CQRS.Commands;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Http.HttpResults;

namespace backend.Services
{
    public class AuthService
    {
        private readonly ApplicationDbContext _context;
        private readonly IConfiguration _config;


        public AuthService(ApplicationDbContext context, IConfiguration config)
        {
            _context = context;
            _config = config;
        }

        public async Task<string> RegisterUserAsync(RegisterUserCommand command)
        {
            // Check if user already exists
            var exists = await _context.Users.AnyAsync(u => u.Username == command.Username);
            if (exists)
                throw new Exception("Username already exists.");

            // Hash the password
            var hashedPassword = BCrypt.Net.BCrypt.HashPassword(command.Password);

            // Create user
            var user = new User
            {
                Id = Guid.NewGuid(),
                Username = command.Username,
                PasswordHash = hashedPassword
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            return user.Id.ToString();

        }


        public async Task<Guid> LoginAsync(string username, string password)
        {
            var user = await _context.Users.FirstOrDefaultAsync(u => u.Username == username);
            if (user == null)
                throw new Exception("User not found");

            var isValid = BCrypt.Net.BCrypt.Verify(password, user.PasswordHash);
            if (!isValid)
                throw new Exception("Invalid password");

            return user.Id;
        }


    }
}
