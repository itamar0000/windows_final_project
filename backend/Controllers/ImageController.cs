using Microsoft.AspNetCore.Mvc;
using backend.Services;
using Microsoft.AspNetCore.Http;
using System.Threading.Tasks;
using backend.Data;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ImageController : ControllerBase
    {
        private readonly ImageService _imageService;
        private readonly ApplicationDbContext _context;


        public ImageController(ImageService imageService)
        {
            _imageService = imageService;
        }
        public ImageController(ImageService imageService, ApplicationDbContext context)
        {
            _imageService = imageService;
            _context = context;
        }

        [HttpPost("upload")]
        public async Task<IActionResult> Upload([FromForm] IFormFile file, [FromForm] string userId)
        {
            if (file == null || string.IsNullOrEmpty(userId))
                return BadRequest("File and userId are required.");

            var url = await _imageService.UploadImageAsync(file, userId);
            if (url == null)
                return StatusCode(500, "Image upload failed");

            // ✅ Save to the user in the DB
            var userGuid = Guid.Parse(userId);
            var user = await _context.Users.FindAsync(userGuid);

            if (user == null)
                return NotFound("User not found.");

            user.ProfileImageUrl = url;
            await _context.SaveChangesAsync();

            return Ok(new { url });
        }


    }
}
