from interfaces import ILoginView, IPortfolioView, IAuthService, IPortfolioService, IAiChatView
from model import Portfolio
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, QThread, Signal
from services import ApiClient


# --- Login Presenter ---
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QMessageBox
from interfaces import ILoginView, IAuthService

class LoginWorker(QObject):
    login_finished = Signal(bool, str)  # success, userId or error message
    signup_finished = Signal(bool, str)  # success, userId or error message

    def __init__(self, auth_service: IAuthService, username: str, password: str, is_login: bool):
        super().__init__()
        self.auth_service = auth_service
        self.username = username
        self.password = password
        self.is_login = is_login

    def run(self):
        try:
            if self.is_login:
                success = self.auth_service.authenticate(self.username, self.password)
                if success:
                    user_id = self.auth_service.get_user_id()
                    self.login_finished.emit(True, user_id)
                else:
                    self.login_finished.emit(False, "Invalid username or password")
            else:
                success = self.auth_service.register(self.username, self.password)
                if success:
                    user_id = self.auth_service.get_user_id()
                    self.signup_finished.emit(True, user_id)
                else:
                    self.signup_finished.emit(False, "Username already exists or failed to register")
        except Exception as e:
            if self.is_login:
                self.login_finished.emit(False, str(e))
            else:
                self.signup_finished.emit(False, str(e))


class LoginPresenter(QObject):
    def __init__(self, view: ILoginView, auth_service: IAuthService):
        super().__init__()
        self.view = view
        self.auth_service = auth_service

        self.view.login_requested.connect(self.handle_login)
        self.view.signup_requested.connect(self.handle_signup)

    def handle_login(self, username: str, password: str):
        self.worker = LoginWorker(self.auth_service, username, password, is_login=True)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.login_finished.connect(self.login_result)
        self.worker.login_finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_signup(self, username: str, password: str):
        self.worker = LoginWorker(self.auth_service, username, password, is_login=False)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.signup_finished.connect(self.signup_result)
        self.worker.signup_finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def login_result(self, success: bool, message: str):
        if success:
            self.view.clear_inputs()
            self.view.login_successful.emit(message)
        else:
            self.show_error(message)

    def signup_result(self, success: bool, message: str):
        if success:
            self.view.clear_inputs()
            self.view.login_successful.emit(message)
        else:
            self.show_error(message)

    def show_error(self, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()


# --- Portfolio Presenter ---
class PortfolioPresenter:
    def __init__(self, view: IPortfolioView, portfolio_service: IPortfolioService, user_id: str):
        self.view = view
        self.service = portfolio_service
        self.current_user_id = user_id

        self.view.stock_search_requested.connect(self.handle_stock_search)
        self.view.buy_requested.connect(self.handle_buy)
        self.view.sell_requested.connect(self.handle_sell)

    def load_portfolio(self):
        portfolio = self.service.get_portfolio(self.current_user_id)
        self.view.set_username(portfolio.user.username)

        profile_titles = [
            "The Default", "Risk Taker", "Business Savvy", "The Analyst",
            "Growth Guru", "Steady Saver", "Market Hawk", "The Bull", "The Bear"
        ]

        profile_index = 0
        url = portfolio.user.profileImageUrl or ""
        if "profile_" in url:
            try:
                name = url.split("profile_")[1].split(".")[0]
                profile_index = 0 if name == "default" else int(name)
            except:
                profile_index = 0

        self.view.set_profile_title(profile_titles[profile_index])
        self.view.update_portfolio_summary(
            portfolio.total_value,
            self._calculate_daily_change(portfolio)
        )
        total_gain = sum(stock.gain_loss for stock in portfolio.stocks)
        self.view.update_total_gain_loss(total_gain)
        self.view.update_holdings_table(portfolio.stocks)
        self.view.update_transaction_history(portfolio.transactions)

    def _calculate_daily_change(self, portfolio: Portfolio) -> float:
        return 2.5

    def handle_buy(self, symbol: str, shares: int):
        if self.service.execute_buy_order(self.current_user_id, symbol, shares):
            self.load_portfolio()
        else:
            self.view.show_error("Failed to execute buy order")

    def handle_sell(self, symbol: str, shares: int):
        if self.service.execute_sell_order(self.current_user_id, symbol, shares):
            self.load_portfolio()
        else:
            self.view.show_error("Failed to execute sell order")

    def handle_stock_search(self, symbol: str, period: str):
        try:
            history, name, price = self.service.get_stock_data(symbol, period)
            self.view.update_stock_search_result(name, price, history)
        except Exception as e:
            print("Stock search failed:", e)
            self.view.update_stock_search_result("Error", 0.0, [])


# --- AI Chat Presenter ---
class AiWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, service: ApiClient, message: str, user_id: str):
        super().__init__()
        self.service = service
        self.message = message
        self.user_id = user_id

    def run(self):
        try:
            # Ask the AI using ApiClient
            answer = self.service.ask(self.message)
            self.finished.emit(answer)
        except Exception as e:
            self.error.emit(str(e))


class AiChatPresenter(QObject):
    def __init__(self, view: IAiChatView, api_client: ApiClient, user_id: str):
        super().__init__()
        self.view = view
        self.api_client = api_client
        self.user_id = user_id

        self.view.send_message_requested.connect(self.handle_send_message)

    def handle_send_message(self, message: str):
        if not message.strip():
            return

        self.view.add_message(message, from_user=True)
        self.view.set_typing_indicator(True)

        self.worker = AiWorker(self.api_client, message, self.user_id)
        self.thread = QThread()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.error.connect(self.handle_ai_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

    def handle_ai_response(self, response: str):
        self.view.set_typing_indicator(False)
        self.view.add_message(response, from_user=False)

    def handle_ai_error(self, error_message: str):
        self.view.set_typing_indicator(False)
        self.view.add_message(f"Error: {error_message}", from_user=False)
