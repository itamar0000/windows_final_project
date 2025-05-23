﻿using System.Reflection;
using System.IO;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using backend.Data;
using backend.Services;
using CloudinaryDotNet;


namespace backend
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Load configuration
            builder.Configuration.AddJsonFile("config/appsettings.json", optional: false, reloadOnChange: true);

            // Configure Database
            builder.Services.AddDbContext<ApplicationDbContext>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

            // Register Application Services
            builder.Services.AddScoped<AuthService>();
            builder.Services.AddScoped<PortfolioService>();
            builder.Services.AddScoped<StockService>();
            builder.Services.AddScoped<ImageService>();
            builder.Services.AddHttpClient<AiAdvisorService>();

            builder.Services.AddSingleton(_ =>
            {
                var account = new Account(
                    "dxohlu5cy",                      // Cloud name
                    "527676832721251",                // API Key
                    "Z5Fczs4Wq3uGv9oLof22g3QWzds"      // API Secret
                );
                return new Cloudinary(account);
            });

            // Enable Controllers
            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();

            // Configure Swagger (no JWT)
            builder.Services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title = "Stock Portfolio Management API",
                    Version = "v1",
                    Description = "An API for managing stock portfolios, including buying/selling stocks and AI-powered investment analysis.",
                    Contact = new OpenApiContact
                    {
                        Name = "Your Name",
                        Email = "your.email@example.com",
                        Url = new Uri("https://yourwebsite.com")
                    },
                    License = new OpenApiLicense
                    {
                        Name = "MIT License",
                        Url = new Uri("https://opensource.org/licenses/MIT")
                    }
                });

                // Include XML comments (optional)
                var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
                var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
                if (File.Exists(xmlPath))
                {
                    c.IncludeXmlComments(xmlPath);
                }
            });

            var app = builder.Build();
            
            //////////////////////////
            //var scope = app.Services.CreateScope();
            //var imageService = scope.ServiceProvider.GetRequiredService<ImageService>();

            //var defaultUrl = imageService.UploadDefaultProfileImage();
            //Console.WriteLine("✅ Default profile image uploaded:");
            //Console.WriteLine(defaultUrl);
            //var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
            //var users = context.Users.ToList();
            //foreach (var user in users)
            //{
            //    user.ProfileImageUrl = defaultUrl;
            //}
            //context.SaveChanges();
            //Console.WriteLine("✅ All users updated with default image.");

            /////////////////////////////////
            // Enable Swagger UI
            app.UseSwagger();
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "Stock Portfolio Management API v1");
                c.DocumentTitle = "Stock Portfolio API Docs";
            });

            app.UseHttpsRedirection();

            // No authentication
            app.UseAuthorization();

            app.MapControllers();

            app.Run();



        }
    }
}
