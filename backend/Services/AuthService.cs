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
        private readonly string _defaultProfileImageUrl;



        public AuthService(ApplicationDbContext context, IConfiguration config)
        {
            _context = context;
            _config = config;
            _defaultProfileImageUrl = config["Cloudinary:DefaultProfileImageUrl"];

        }

        public async Task<Guid> RegisterUserAsync(RegisterUserCommand command)
        {
            var existingUser = await _context.Users.FirstOrDefaultAsync(u => u.Username == command.Username);
            if (existingUser != null)
                throw new Exception("Username already taken");

            var user = new User
            {
                Id = Guid.NewGuid(),
                Username = command.Username,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(command.Password),
                ProfileImageUrl = _defaultProfileImageUrl
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            return user.Id;
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
