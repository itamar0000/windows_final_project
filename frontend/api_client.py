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
        print("Raw portfolio data:", data)

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

        # Group transactions by symbol
        tx_by_symbol = {}
        for t in transactions:
            if t.action_type == "Buy":
                tx_by_symbol.setdefault(t.symbol, []).append(t)

        stocks = []
        for stock in data.get("stocks", []):
            symbol = stock["symbol"]
            shares = stock["shares"]

            # Compute average purchase price
            txs = tx_by_symbol.get(symbol, [])
            total_shares = sum(t.shares for t in txs)
            total_cost = sum(t.shares * t.price for t in txs)
            purchase_price = (total_cost / total_shares) if total_shares > 0 else 0

            try:
                price_res = requests.get(f"{self.base_url}/api/Stock/{symbol}/price")
                price_res.raise_for_status()
                current_price = price_res.json()["price"]
            except:
                print(f"Failed to get live price for {symbol}")
                current_price = purchase_price

            stocks.append(Stock(
                symbol=symbol,
                shares=shares,
                purchase_price=purchase_price,
                current_price=current_price
            ))

        user_data = data.get("user")
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            passwordHash="",
            profileImageUrl=user_data.get("profileImageUrl")
        )

        return Portfolio(
            user=user,
            stocks=stocks,
            last_updated=datetime.now(),
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


    # def ask_question(self, question: str) -> str:
    #     """Send a question to the AI Advisor backend and get the answer."""
    #     url = f"{self.base_url}/api/aiadvisor/ask"
    #     payload = {"question": question}

    #     response = requests.post(url, json=payload, timeout=120)
    #     if response.status_code != 200:
    #         raise Exception(f"AI Advisor API error: {response.status_code}")

    #     data = response.json()
    #     return data.get("response", "No answer received.")
    
    async def ask_ai(self, user_id: str, question: str) -> str:
        url = f"{self.base_url}/api/AiAdvisor/ask"
        try:
            payload = {
                "question": question
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "No response received from AI.")
        except Exception as e:
            return f"Error: {e}"
