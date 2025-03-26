from interfaces import ILoginView, IPortfolioView, IAuthService, IPortfolioService
from model import Portfolio
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from interfaces import IPortfolioView, IPortfolioService
from model import Portfolio


class LoginPresenter:
    def __init__(self, view: ILoginView, auth_service: IAuthService):
        self.view = view
        self.auth_service = auth_service

        self.view.login_requested.connect(self.handle_login)
        self.view.signup_requested.connect(self.handle_signup)
        


    def handle_login(self, username: str, password: str):
        """Handles login attempt and updates UI accordingly."""
        if self.auth_service.authenticate(username, password):
            self.view.clear_inputs()
            self.view.login_successful.emit(self.auth_service.get_user_id())
        else:
            self.show_error("Invalid username or password")

    def handle_signup(self, username: str, password: str):
        """Handles user registration."""
        if self.auth_service.register(username, password):
            self.view.clear_inputs()
            self.view.login_successful.emit(self.auth_service.get_user_id())
        else:
            self.show_error("Username already exists or failed to register.")

    def show_error(self, message):
        """Display error message in a popup."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Login Failed")
        msg_box.setText(message)
        msg_box.exec()



class PortfolioPresenter:
    def __init__(self, view: IPortfolioView, portfolio_service: IPortfolioService, user_id: str):
        self.view = view
        self.service = portfolio_service
        self.current_user_id = user_id  # ✅ Now real user!


        # Connect UI signals to functions
        self.view.buy_requested.connect(self.handle_buy)
        self.view.sell_requested.connect(self.handle_sell)

    def load_portfolio(self):
        """Fetches portfolio data and updates the UI."""
        portfolio = self.service.get_portfolio(self.current_user_id)
        self.view.update_portfolio_summary(
            portfolio.total_value,
            self._calculate_daily_change(portfolio)
        )
        self.view.update_holdings_table(portfolio.stocks)

    def _calculate_daily_change(self, portfolio: Portfolio) -> float:
        """Mock function to simulate daily change percentage."""
        return 2.5  # Static value for now

    def handle_buy(self, symbol: str, shares: int):
        """Handles buy transactions."""
        if self.service.execute_buy_order(self.current_user_id, symbol, shares):
            self.load_portfolio()  # Refresh UI after transaction
        else:
            self.view.show_error("Failed to execute buy order")

    def handle_sell(self, symbol: str, shares: int):
        """Handles sell transactions."""
        if self.service.execute_sell_order(self.current_user_id, symbol, shares):
            self.load_portfolio()  # Refresh UI after transaction
        else:
            self.view.show_error("Failed to execute sell order")
