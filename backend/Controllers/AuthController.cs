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

        public AuthController(AuthService authService)
        {
            _authService = authService;
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

  


    }

    public class AuthRequest
    {
        public string Username { get; set; }
        public string Password { get; set; }
    }
}
