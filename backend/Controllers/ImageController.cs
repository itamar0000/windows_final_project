﻿using Microsoft.AspNetCore.Mvc;
using backend.Services;
using Microsoft.AspNetCore.Http;
using System.Threading.Tasks;
using backend.Data;
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


        [HttpPost("upload")]
        public async Task<IActionResult> Upload([FromForm] IFormFile file, [FromForm] string userId)
        {
            if (file == null || string.IsNullOrEmpty(userId))
                return BadRequest("File and userId are required.");

            if (!Guid.TryParse(userId, out var userGuid))
                return BadRequest("Invalid userId format.");

            var url = await _imageService.UploadImageAsync(file, userId);
            if (string.IsNullOrEmpty(url))
                return StatusCode(500, "Image upload failed");

            var user = await _context.Users.FindAsync(userGuid);
            if (user == null)
                return NotFound("User not found.");

            user.ProfileImageUrl = url;
            await _context.SaveChangesAsync();

            return Ok(new { message = "✅ Upload successful", url });
        }


    }
}
