# services.py
from datetime import datetime
import requests
from api_client import ApiClient
from model import Portfolio
from interfaces import IAuthService, IPortfolioService
from interfaces import IStockService
from typing import List
from datetime import datetime
from model import Portfolio, Stock
from interfaces import IPortfolioService


class AuthService(IAuthService):
    def __init__(self):
        self.api_client = ApiClient("http://localhost:5000")
        self.user_id = None

    def authenticate(self, username: str, password: str) -> bool:
        self.user_id = self.api_client.login(username, password)
        return self.user_id is not None

    def register(self, username: str, password: str) -> bool:
        self.user_id = self.api_client.register(username, password)
        return self.user_id is not None

    def get_user_id(self):
        return self.user_id


class PortfolioService(IPortfolioService):
    def __init__(self):
        # Mock portfolio data (instead of fetching from an API)
        self.mock_portfolio = Portfolio(
            stocks=[
                Stock(symbol="AAPL", shares=10, current_price=150.00),
                Stock(symbol="TSLA", shares=5, current_price=700.00),
                Stock(symbol="GOOGL", shares=2, current_price=2800.00),
            ],
            last_updated=datetime.now()
        )

    def get_portfolio(self, user_id: str) -> Portfolio:
        """Returns mock portfolio data."""
        return self.mock_portfolio

    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool:
        """Mock buy order - adds shares to portfolio."""
        for stock in self.mock_portfolio.stocks:
            if stock.symbol == symbol:
                stock.shares += shares
                return True  # Successful purchase
        
        # If stock is new, add it to the portfolio
        self.mock_portfolio.stocks.append(Stock(symbol=symbol, shares=shares, current_price=100.00))  
        return True

    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool:
        """Mock sell order - removes shares from portfolio."""
        for stock in self.mock_portfolio.stocks:
            if stock.symbol == symbol:
                if stock.shares >= shares:
                    stock.shares -= shares
                    return True  # Successful sale
                else:
                    return False  # Not enough shares
        
        return False  # Stock not found in portfolio

"""
class PortfolioService(IPortfolioService):
    def __init__(self):
        self.api_client = ApiClient("https://your-api-url")

    def get_portfolio(self, user_id: str) -> Portfolio:
        return self.api_client.get_portfolio(user_id)

    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool:
        return self.api_client.execute_buy_order(user_id, symbol, shares)

    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool:
        return self.api_client.execute_sell_order(user_id, symbol, shares)
    """
class StockService(IStockService):
    def __init__(self):
        self.api_client = ApiClient("https://your-api-url")
    
    def get_stock_data(self, symbol: str) -> tuple[List[tuple[datetime, float]], str, float]:
        return self.api_client.get_stock_data(symbol)
    
    def search_stock(self, query: str) -> List[tuple[str, str]]:
        return self.api_client.search_stock(query)

# api_client.py - Add these new methods
def get_stock_data(self, symbol: str) -> tuple[List[tuple[datetime, float]], str, float]:
    response = requests.get(
        f"{self.base_url}/api/stocks/{symbol}",
        headers={"Authorization": f"Bearer {self.token}"}
    )
    data = response.json()
    return (
        [(datetime.fromisoformat(point["date"]), point["price"]) for point in data["history"]],
        data["name"],
        data["current_price"]
    )

def search_stock(self, query: str) -> List[tuple[str, str]]:
    response = requests.get(
        f"{self.base_url}/api/stocks/search",
        params={"q": query},
        headers={"Authorization": f"Bearer {self.token}"}
    )
    results = response.json()
    return [(item["symbol"], item["name"]) for item in results]
