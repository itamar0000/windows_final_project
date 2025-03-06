# services.py
from datetime import datetime

import requests
from api_client import ApiClient
from frontend.model import Portfolio
from frontend.interfaces import IAuthService, IPortfolioService


class AuthService(IAuthService):
    def __init__(self):
        self.api_client = ApiClient("https://your-api-url")
    
    def authenticate(self, username: str, password: str) -> bool:
        return self.api_client.login(username, password)

class PortfolioService(IPortfolioService):
    def __init__(self):
        self.api_client = ApiClient("https://your-api-url")

    def get_portfolio(self, user_id: str) -> Portfolio:
        return self.api_client.get_portfolio(user_id)

    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool:
        return self.api_client.execute_buy_order(user_id, symbol, shares)

    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool:
        return self.api_client.execute_sell_order(user_id, symbol, shares)
    
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
