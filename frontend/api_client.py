# api_client.py
import datetime
import requests
from typing import Optional
from model import Portfolio, Stock, User, Transaction
from datetime import datetime
from datetime import datetime, timedelta

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
        response = requests.get(f"{self.base_url}/api/portfolio/{user_id}")
        if response.status_code != 200:
            print(f"Portfolio API error: {response.status_code}")
            raise Exception("Portfolio not found")

        data = response.json()
        print("Raw portfolio data:", data)  # See the actual JSON response

        # Make sure you're handling the stocks correctly
        stocks = []
        if "stocks" in data and data["stocks"]:
            stocks = [
                Stock(
                    symbol=stock["symbol"],
                    shares=stock["shares"],
                    current_price=stock["currentPrice"]
                )
                for stock in data["stocks"]
            ]
        
        transactions = [
            Transaction(
                symbol=t["symbol"],
                shares=t["shares"],
                price=t["price"],
                action_type=t["actionType"],
                timestamp=t.get("timestamp", "")
            )
            for t in data.get("transactions", [])
        ]
        print(f"Parsed {len(stocks)} stocks from API response")
        # Fallback if lastUpdated doesn't exist
        last_updated = datetime.now()

        user_data = data.get("user")
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            passwordHash="",  # you can leave this blank since it's not needed on frontend
            profileImageUrl=user_data.get("profileImageUrl")
        )

        return Portfolio(
            user=user,
            stocks=stocks,
            last_updated=last_updated,
            transactions=transactions
        )


    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool:
        response = requests.post(
            f"{self.base_url}/api/Stock/buy",
            json={"userId": user_id, "symbol": symbol, "shares": shares}
        )
        return response.ok

    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool:
        response = requests.post(
            f"{self.base_url}/api/Stock/sell",
            json={"userId": user_id, "symbol": symbol, "shares": shares}
        )
        return response.ok


    def get_profile_image(self, user_id: str) -> str | None:
        response = requests.get(f"{self.base_url}/api/Image/profile-image/{user_id}")
        if response.status_code == 200:
            return f"{self.base_url}/api/Image/profile-image/{user_id}"  # since it returns raw image
        return None

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



    def get_stock_data(self, symbol: str, period: str) -> tuple[list[tuple[datetime, float]], str, float]:
        # Get full history from backend
        history_res = requests.get(f"{self.base_url}/api/Stock/{symbol}/history")
        if history_res.status_code != 200:
            raise Exception("Failed to load history")

        history = [
            (datetime.fromisoformat(p["date"]), p["price"])
            for p in history_res.json()
        ]
        print()
        print("Raw history data:", history)  # Debugging line
        # Apply filtering by time period
        now = datetime.now()
        period_map = {
            "1D": timedelta(days=1),
            "1W": timedelta(weeks=1),
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "6M": timedelta(days=180),
            "1Y": timedelta(days=365),
            "5Y": timedelta(days=5*365),
            "10Y": timedelta(days=10*365)
        }
        if period in period_map:
            start_date = now - period_map[period]
            history = [(d, p) for d, p in history if d >= start_date]

        # Get current price
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
    
    def get_username(self, user_id: str) -> str:
        response = requests.get(f"{self.base_url}/api/Auth/user/{user_id}")
        if response.status_code == 200:
            return response.json().get("username", "Unknown")
        return "Unknown"
