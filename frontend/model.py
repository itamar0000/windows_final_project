# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Stock:
    symbol: str
    shares: int
    purchase_price: float
    current_price: float

    @property
    def value(self) -> float:
        return self.shares * self.current_price

    @property
    def gain_loss(self) -> float:
        return (self.current_price - self.purchase_price) * self.shares


@dataclass
class Transaction:
    symbol: str
    shares: int
    price: float
    action_type: str
    timestamp: str  # Keep as str unless you want to parse it as `datetime`

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
    transactions: List[Transaction]

    @property
    def total_value(self) -> float:
        return sum(stock.value for stock in self.stocks)
