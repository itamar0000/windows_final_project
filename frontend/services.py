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
        self.api_client = ApiClient("http://localhost:5000")  # ✅ URL is here

    def get_profile_image(self, user_id: str) -> str | None:
        return self.api_client.get_profile_image(user_id)

    def get_portfolio(self, user_id: str) -> Portfolio:
        return self.api_client.get_portfolio(user_id)  # ✅ call through ApiClient

    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool:
        return self.api_client.execute_buy_order(user_id, symbol, shares)

    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool:
        return self.api_client.execute_sell_order(user_id, symbol, shares)
    
    def get_username(self, user_id: str) -> str:
        return self.api_client.get_username(user_id)
    
    def get_stock_data(self, symbol: str, period: str) -> tuple[list[tuple[datetime, float]], str, float]:
        return self.api_client.get_stock_data(symbol, period)






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
        self.api_client = ApiClient("http://localhost:5000")
    
    def get_stock_data(self, symbol: str) -> tuple[List[tuple[datetime, float]], str, float]:
        return self.api_client.get_stock_data(symbol)
    
    def search_stock(self, query: str) -> List[tuple[str, str]]:
        return self.api_client.search_stock(query)

def get_stock_data(self, symbol: str) -> tuple[List[tuple[datetime, float]], str, float]:
    response = requests.get(f"{self.base_url}/api/stocks/{symbol}")
    data = response.json()
    return (
        [(datetime.fromisoformat(point["date"]), point["price"]) for point in data["history"]],
        data["name"],
        data["current_price"]
    )

def search_stock(self, query: str) -> List[tuple[str, str]]:
    response = requests.get(
        f"{self.base_url}/api/stocks/search",
        params={"q": query}
    )
    results = response.json()
    return [(item["symbol"], item["name"]) for item in results]

from interfaces import IAiAdvisorService

class AiAdvisorService(IAiAdvisorService):
    def __init__(self):
        self.api_client = ApiClient("http://localhost:5000")

    def ask(self, message):
        try:
            response = requests.post(
                "http://localhost:5000/api/AiAdvisor/ask",
                json={"question": message}  # ✅ no userId needed
            )
            data = response.json()
            return data["response"]  # ✅ get "response", not "answer"
        except Exception as e:
            print("AI ask error:", e)
            return f"Error: {e}"