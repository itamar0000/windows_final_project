using Microsoft.AspNetCore.Mvc;
using backend.Services;
using Microsoft.AspNetCore.Http;
using System.Threading.Tasks;
using backend.Data;
using backend.Services;
using System.ComponentModel.DataAnnotations;


namespace backend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ImageController : ControllerBase
    {
        private readonly ImageService _imageService;
        private readonly ApplicationDbContext _context;


        public ImageController(ImageService imageService, ApplicationDbContext context)
        {
            _imageService = imageService;
            _context = context;
        }

        public class ImageUploadRequest
        {
            [Required]
            public IFormFile File { get; set; }

            [Required]
            public string UserId { get; set; }
        }


        [HttpPost("set-preset")]
        public async Task<IActionResult> SetPresetImage([FromForm] string userId, [FromForm] int presetIndex)
        {
            if (!Guid.TryParse(userId, out var userGuid))
                return BadRequest("Invalid userId format.");

            if (presetIndex < 0 || presetIndex > 8)
                return BadRequest("Preset index must be between 0 and 8.");

            var imageUrl = await _imageService.GetPresetImageUrl(presetIndex); // ✅ FIXED

            var user = await _context.Users.FindAsync(userGuid);
            if (user == null)
                return NotFound("User not found.");

            user.ProfileImageUrl = imageUrl;
            await _context.SaveChangesAsync();

            return Ok(new { message = "✅ Preset image set", imageUrl });
        }



        [HttpGet("profile-image/{userId}")]
        public async Task<IActionResult> GetProfileImage(Guid userId)
        {
            try
            {
                var imageUrl = await _imageService.GetProfileImageUrlAsync(userId);
                if (string.IsNullOrEmpty(imageUrl))
                    return NotFound("No image found for the user.");

                using var httpClient = new HttpClient();
                var imageBytes = await httpClient.GetByteArrayAsync(imageUrl);

                return File(imageBytes, "image/png");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"🔥 ERROR: {ex.Message}");
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("image-presets/{index}")]
        public async Task<IActionResult> GetPresetImages(int index)
        {
            try
            {
                var imageUrl = await _imageService.GetPresetImageUrl(index); // ✅ now imageUrl is string
                if (string.IsNullOrEmpty(imageUrl))
                    return NotFound("No image found for the index.");

                using var httpClient = new HttpClient();
                var imageBytes = await httpClient.GetByteArrayAsync(imageUrl);

                return File(imageBytes, "image/png");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"🔥 ERROR: {ex.Message}");
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }


    }
}
