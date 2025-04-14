# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Stock:
    def __init__(self, symbol: str, shares: int, current_price: float):
        self.symbol = symbol
        self.shares = shares
        self.current_price = current_price
    
    @property
    def value(self) -> float:
        return self.shares * self.current_price

@dataclass
class User:
    id: str
    username: str
    passwordHash: str
    profileImageUrl: Optional[str] = None

@dataclass
class Portfolio:
    user: User
    stocks: List[Stock]
    last_updated: datetime

    @property
    def total_value(self) -> float:
        return sum(stock.value for stock in self.stocks)