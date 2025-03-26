# api_client.py
import datetime
import requests
from typing import Optional
from model import Portfolio, Stock

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def login(self, username: str, password: str) -> str | None:
        response = requests.post(
            f"{self.base_url}/api/Auth/login",
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            return response.json()["userId"]  # ← this is from your backend
        else:
            return None
        
    def register(self, username: str, password: str) -> str | None:
        response = requests.post(
            f"{self.base_url}/api/Auth/register",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["userId"]
        return None



    def get_portfolio(self, user_id: str) -> Portfolio:
        response = requests.get(
            f"{self.base_url}/api/portfolio/{user_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        data = response.json()
        return Portfolio(
            stocks=[Stock(**stock) for stock in data["stocks"]],
            last_updated=datetime.fromisoformat(data["lastUpdated"])
        )

    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool:
        response = requests.post(
            f"{self.base_url}/api/orders/buy",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "userId": user_id,
                "symbol": symbol,
                "shares": shares
            }
        )
        return response.ok

    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool:
        response = requests.post(
            f"{self.base_url}/api/orders/sell",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "userId": user_id,
                "symbol": symbol,
                "shares": shares
            }
        )
        return response.ok