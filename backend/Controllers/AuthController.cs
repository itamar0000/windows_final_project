using backend.Services;
using Microsoft.AspNetCore.Mvc;
using backend.Models;
using backend.CQRS.Commands;
using backend.Data;
using Microsoft.EntityFrameworkCore;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly AuthService _authService;
        private readonly ApplicationDbContext _context;

        public AuthController(AuthService authService, ApplicationDbContext context)
        {
            _authService = authService;
            _context = context;
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register([FromBody] RegisterUserCommand command)
        {
            try
            {
                var userId = await _authService.RegisterUserAsync(command);
                return Ok(new { userId });
            }
            catch (Exception ex)
            {
                return BadRequest(new { error = ex.Message });
            }
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] AuthRequest request)
        {
            try
            {
                var userId = await _authService.LoginAsync(request.Username, request.Password);
                return Ok(new { userId });
            }
            catch (Exception ex)
            {
                return BadRequest(new { error = ex.Message });
            }
        }

        // ? GET /api/auth/{id}
        [HttpGet("{id}")]
        public async Task<IActionResult> GetUser(Guid id)
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
                return NotFound();

            return Ok(new
            {
                id = user.Id,
                username = user.Username,
                profileImageUrl = string.IsNullOrEmpty(user.ProfileImageUrl) ? null : user.ProfileImageUrl
            });
        }

        // ? PUT /api/auth/{id}/profile-image
        [HttpPut("{id}/profile-image")]
        public async Task<IActionResult> UpdateProfileImage(Guid id, [FromBody] string imageUrl)
        {
            var user = await _context.Users.FindAsync(id);
            if (user == null)
                return NotFound();

            user.ProfileImageUrl = imageUrl;
            await _context.SaveChangesAsync();

            return Ok(new { message = "Profile image updated", url = imageUrl });
        }
    }

    public class AuthRequest
    {
        public string Username { get; set; }
        public string Password { get; set; }
    }
}
