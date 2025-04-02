# api_client.py
import datetime
import requests
from typing import Optional
from model import Portfolio, Stock
from datetime import datetime

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
    
    def upload_profile_image(self, user_id: str, file_path: str) -> str | None:
        with open(file_path, 'rb') as image_file:
            files = {'file': (file_path, image_file, 'multipart/form-data')}
            response = requests.post(
                f"{self.base_url}/api/Auth/{user_id}/upload-image",
                files=files
            )
        if response.status_code == 200:
            return response.json().get("imageUrl")
        return None

    def get_profile_image(self, user_id: str) -> str:
        response = requests.get(f"{self.base_url}/api/Auth/user/{user_id}/image")
        if response.status_code == 200:
            return response.json().get("imageUrl")
        return None


    def get_stock_data(self, symbol: str) -> tuple[list[tuple[datetime, float]], str, float]:
        history_res = requests.get(f"{self.base_url}/api/Stock/{symbol}/history")
        if history_res.status_code != 200:
            raise Exception("Failed to load history")

        history = [
            (datetime.fromisoformat(p["date"]), p["price"])
            for p in history_res.json()
        ]

        price_res = requests.get(f"{self.base_url}/api/Stock/{symbol}/price")
        if price_res.status_code != 200:
            raise Exception("Failed to load price")

        price = price_res.json()["price"]

        return history, symbol.upper(), price

def search_stock(self, query: str) -> list[tuple[str, str]]:
    # If you have a real endpoint for searching stock symbols and names
    res = requests.get(f"{self.base_url}/api/Stock/search", params={"q": query})
    if res.status_code != 200:
        return []

    return [(item["symbol"], item["name"]) for item in res.json()]
