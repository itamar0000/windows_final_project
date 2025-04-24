backend/
 ┣ 📂 Config/
 ┃ ┗ 📄 appsettings.json
 ┃     🔹 Contains configuration for:
 ┃         - Cloudinary API keys
 ┃         - TwelveData API key
 ┃         - Database connection string
 ┃         - Any other third-party service config
 ┃     🔹 Used by IConfiguration throughout the app
 ┣ 📂 Controllers/
 ┃ ┣ 📄 AuthController.cs
 ┃     🔹 Handles user registration, login
 ┃     🔹 New: GET user by ID, update profile image URL
 ┃
 ┃ ┣ 📄 PortfolioController.cs
 ┃     🔹 Returns the current portfolio and transactions
 ┃     🔹 Uses EF with eager loading of Stocks & Transactions
 ┃
 ┃ ┣ 📄 StockController.cs
 ┃     🔹 Fetches live and historical stock data from TwelveData
 ┃     🔹 Maps /api/stock endpoints (e.g., `/history`, `/price`)
 ┃
 ┃ ┣ 📄 ImageController.cs
 ┃     🔹 Accepts user image uploads via `IFormFile`
 ┃     🔹 Calls Cloudinary and stores image per user
 ┃
 ┃ ┗ 📄 AiAdvisorController.cs *(optional/next phase)*
 ┃     🔹 Accepts questions to ask your Ollama RAG server
 ┃     🔹 Returns AI-generated advice for stocks
 ┣ 📂 CQRS/
 ┃ ┣ 📂 Commands/
 ┃ ┃ ┣ 📄 BuyStockCommand.cs
 ┃ ┃ ┃ 🔹 Encapsulates parameters for a Buy operation (symbol, shares, userId)
 ┃ ┃ ┗ 📄 SellStockCommand.cs
 ┃ ┃ ┃ 🔹 Same, but for selling stocks
 ┃
 ┃ ┣ 📂 Queries/
 ┃ ┃ ┣ 📄 GetPortfolioQuery.cs
 ┃ ┃ ┃ 🔹 Used to fetch portfolio (delegates to a query handler)
 ┃ ┃ ┣ 📄 GetStockPriceQuery.cs
 ┃ ┃ ┃ 🔹 Used to fetch current stock price
 ┃ ┃ ┗ 📄 GetStockHistoryQuery.cs
 ┃ ┃ ┃ 🔹 (Optional) If you use a CQRS wrapper around history
 ┃
 ┃ ┗ 📄 MediatorSetup.cs
 ┃     🔹 Registers all command & query handlers with the DI container
 ┣ 📂 Data/
 ┃ ┣ 📂 Migrations/
 ┃ ┃ ┗ 📄 *_AddProfileImageUrl.cs
 ┃ ┃     🔹 EF Core migrations for schema changes
 ┃
 ┃ ┣ 📄 ApplicationDbContext.cs
 ┃ ┃ 🔹 The main DbContext for Users, Portfolios, Stocks, Transactions
 ┃
 ┃ ┣ 📄 EventStoreDbContext.cs *(Optional)*
 ┃ ┃ 🔹 If using Event Sourcing — this stores domain events
 ┃
 ┃ ┗ 📄 DataSeeder.cs
 ┃     🔹 Seeds initial users & portfolios for testing/demo
 ┣ 📂 Deployment/
 ┃ ┗ 📄 Dockerfile
 ┃     🔹 Docker container setup for deploying the API
 ┃     🔹 Uses ASP.NET Core base image
 ┣ 📂 EventSourcing/
 ┃ ┣ 📄 EventHandler.cs
 ┃ ┃ 🔹 Handles domain events (Buy, Sell)
 ┃ ┗ 📄 EventStore.cs
 ┃     🔹 Stores event history for each user/portfolio
 ┣ 📂 Gateway/
 ┃ ┣ 📄 ExternalApiGateway.cs
 ┃ ┃ 🔹 Abstracts calls to TwelveData, Cloudinary, etc.
 ┃ ┗ 📄 ServiceRegistry.cs
 ┃     🔹 Stores external service URLs and credentials
 ┣ 📂 Middleware/
 ┃ ┗ 📄 ExceptionMiddleware.cs
 ┃     🔹 Central error handling & logging for HTTP requests
 ┣ 📂 Models/
 ┃ ┣ 📄 User.cs
 ┃ ┃ 🔹 User ID, Username, PasswordHash, ProfileImageUrl
 ┃
 ┃ ┣ 📄 Portfolio.cs
 ┃ ┃ 🔹 Belongs to a User, contains a list of stocks
 ┃
 ┃ ┣ 📄 Stock.cs
 ┃ ┃ 🔹 Represents a stock symbol, current shares & price
 ┃
 ┃ ┣ 📄 Transaction.cs
 ┃ ┃ 🔹 Logs Buy/Sell orders with timestamp, symbol, price
 ┃
 ┃ ┗ 📄 Image.cs *(optional)*
 ┃     🔹 Structure for storing Cloudinary image metadata (if needed)
 ┣ 📂 Services/
 ┃ ┣ 📄 AuthService.cs
 ┃ ┃ 🔹 Handles user registration, login, and password validation
 ┃
 ┃ ┣ 📄 PortfolioService.cs
 ┃ ┃ 🔹 Executes Buy/Sell commands and manages portfolio updates
 ┃
 ┃ ┣ 📄 StockService.cs
 ┃ ┃ 🔹 Calls TwelveData for stock price & historical data
 ┃
 ┃ ┣ 📄 ImageService.cs
 ┃ ┃ 🔹 Uploads images to Cloudinary and returns URL
 ┃
 ┃ ┗ 📄 AiAdvisorService.cs *(optional)*
 ┃     🔹 Sends prompt to Ollama and returns stock advice
 ┣ 📂 Tests/
 ┃ ┣ 📄 AuthServiceTests.cs
 ┃ ┣ 📄 PortfolioServiceTests.cs
 ┃ ┣ 📄 StockServiceTests.cs
 ┃ ┗ 📄 AiAdvisorServiceTests.cs
 ┣ 📄 backend.csproj
 ┃ 🔹 Project file with NuGet references
 ┣ 📄 backend.http
 ┃ 🔹 Handy testing file for HTTP requests (VS Code/JetBrains HTTP client)
 ┣ 📄 guide.txt
 ┃ 🔹 Internal documentation or how-to
 ┣ 📄 Program.cs
 ┃ 🔹 Main entry point; registers services & middleware
 ┣ 📄 README.md
 ┃ 🔹 Project summary & setup instructions
 ┗ 📄 .gitignore
    🔹 Hides bin/obj and secrets from git

