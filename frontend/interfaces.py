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
    def show_error(self, message: str): pass
    def set_profile_image(self, image_url: str): pass  # ✅ Add this line


class IStockService(Protocol):
    def get_stock_data(self, symbol: str) -> tuple[List[tuple[datetime, float]], str, float]: pass
    def search_stock(self, query: str) -> List[tuple[str, str]]: pass

class IAiAdvisorService(Protocol):
    def ask_question(self, question: str) -> str: pass


from typing import Protocol
from model import AiChatMessage

class IAiChatView(Protocol):
    send_message_requested: any  # Signal will be used in real code (temporary as 'any')

    def add_chat_message(self, message: AiChatMessage): pass
    def show_thinking_state(self): pass
    def hide_thinking_state(self): pass
    def show_error(self, message: str): pass
from abc import ABC, abstractmethod

class IAiChatView(ABC):
    @abstractmethod
    def add_user_message(self, text: str):
        pass

    @abstractmethod
    def add_ai_message(self, text: str):
        pass

class IAiAdvisorService(ABC):
    @abstractmethod
    def ask(self, user_id: str, question: str) -> str:
        pass
