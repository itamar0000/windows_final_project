from interfaces import ILoginView, IPortfolioView, IAuthService, IPortfolioService
from model import Portfolio
from datetime import datetime

class LoginPresenter:
    def __init__(self, view: ILoginView, auth_service: IAuthService):
        self.view = view
        self.auth_service = auth_service
        self.view.login_requested.connect(self.handle_login)
    
    def handle_login(self, username: str, password: str):
        if self.auth_service.authenticate(username, password):
            self.view.clear_inputs()
            self.view.login_successful.emit()
        else:
            self.view.show_error("Invalid credentials")

class PortfolioPresenter:
    def __init__(self, view: IPortfolioView, portfolio_service: IPortfolioService):
        self.view = view
        self.service = portfolio_service
        self.current_user_id = "mock_user"  # For demonstration
        self.view.buy_requested.connect(self.handle_buy)
        self.view.sell_requested.connect(self.handle_sell)
        
    def load_portfolio(self):
        portfolio = self.service.get_portfolio(self.current_user_id)
        self.view.update_portfolio_summary(
            portfolio.total_value,
            self._calculate_daily_change(portfolio)
        )
        self.view.update_holdings_table(portfolio.stocks)
        
    def _calculate_daily_change(self, portfolio: Portfolio) -> float:
        # Mock implementation
        return 2.5
        
    def handle_buy(self, symbol: str, shares: int):
        try:
            success = self.service.execute_buy_order(self.current_user_id, symbol, shares)
            if success:
                self.load_portfolio()
            else:
                self.view.show_error("Failed to execute buy order")
        except Exception as e:
            self.view.show_error(str(e))
    
    def handle_sell(self, symbol: str, shares: int):
        try:
            success = self.service.execute_sell_order(self.current_user_id, symbol, shares)
            if success:
                self.load_portfolio()
            else:
                self.view.show_error("Failed to execute sell order")
        except Exception as e:
            self.view.show_error(str(e))