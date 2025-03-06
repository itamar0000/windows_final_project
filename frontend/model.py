# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Stock:
    symbol: str
    shares: int
    current_price: float
    
    @property
    def value(self) -> float:
        return self.shares * self.current_price

@dataclass
class User:
    username: str
    password_hash: str
    
@dataclass
class Portfolio:
    stocks: List[Stock]
    last_updated: datetime
    
    @property
    def total_value(self) -> float:
        return sum(stock.value for stock in self.stocks)

