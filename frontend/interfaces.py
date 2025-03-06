from typing import Protocol, List
from datetime import datetime
from model import Stock, Portfolio

class ILoginView(Protocol):
    def show_error(self, message: str): pass
    def clear_inputs(self): pass
    def get_credentials(self) -> tuple[str, str]: pass

class IPortfolioView(Protocol):
    def update_portfolio_summary(self, total_value: float, daily_change: float): pass
    def update_holdings_table(self, holdings: List[Stock]): pass
    def update_performance_chart(self, data: List[tuple[datetime, float]]): pass
    def show_error(self, message: str): pass

class IAuthService(Protocol):
    def authenticate(self, username: str, password: str) -> bool: pass

class IPortfolioService(Protocol):
    def get_portfolio(self, user_id: str) -> Portfolio: pass
    def execute_buy_order(self, user_id: str, symbol: str, shares: int) -> bool: pass
    def execute_sell_order(self, user_id: str, symbol: str, shares: int) -> bool: pass

class IStockService(Protocol):
    def get_stock_data(self, symbol: str) -> tuple[List[tuple[datetime, float]], str, float]: pass
    def search_stock(self, query: str) -> List[tuple[str, str]]: pass