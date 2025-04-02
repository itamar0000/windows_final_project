using CloudinaryDotNet;
using CloudinaryDotNet.Actions;

namespace backend.Services
{
    public class ImageService
    {
        private readonly Cloudinary _cloudinary;

        public ImageService()
        {
            var account = new Account(
                "dxohlu5cy",                      // Cloud name
                "527676832721251",                // API Key
                "Z5Fczs4Wq3uGv9oLof22g3QWzds"      // API Secret
            );

            _cloudinary = new Cloudinary(account);
            _cloudinary.Api.Secure = true;
        }

        public string UploadDefaultProfileImage()
        {
            var imagePath = Path.Combine("Data", "images", "profile.png");

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

            var uploadResult = _cloudinary.Upload(uploadParams);

            return uploadResult.SecureUrl.AbsoluteUri;
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

    }
}
