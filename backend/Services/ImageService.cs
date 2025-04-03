using CloudinaryDotNet;
using CloudinaryDotNet.Actions;
using backend.Data;


namespace backend.Services
{
    public class ImageService
    {

        private readonly ApplicationDbContext _context;
        private readonly Cloudinary _cloudinary;

        public ImageService(ApplicationDbContext context, Cloudinary cloudinary)
        {
            _context = context;
            _cloudinary = cloudinary;
        }


        public string UploadDefaultProfileImage()
        {
            var imagePath = "C:\\Users\\noams\\OneDrive\\Desktop\\windows_final_project\\windows_final_project\\backend\\Data\\images\\profile.png";

            if (!File.Exists(imagePath))
                throw new FileNotFoundException("Default profile image not found.", imagePath);

            var uploadParams = new ImageUploadParams
            {
                File = new FileDescription(imagePath),
                Folder = "default",
                PublicId = "profile_default",
                Overwrite = true,
                Transformation = new Transformation().Width(500).Height(500).Crop("fill")
            };

            var result = _cloudinary.Upload(uploadParams);
            return result.SecureUrl.ToString();
        }



        public async Task<string> UploadImageAsync(IFormFile file, string userId)
        {
            if (file == null || file.Length == 0)
                return null;

            using var stream = file.OpenReadStream();

            var uploadParams = new ImageUploadParams
            {
                File = new FileDescription(file.FileName, stream),
                Folder = $"users/{userId}", // Save inside Cloudinary folder per user
                Transformation = new Transformation().Width(500).Height(500).Crop("fill")
            };

            var uploadResult = await _cloudinary.UploadAsync(uploadParams);
            return uploadResult.SecureUrl?.ToString();
        }

        public async Task<string?> GetProfileImageUrlAsync(Guid userId)
        {
            var user = await _context.Users.FindAsync(userId);
            return user?.ProfileImageUrl;
        }



    }
}
