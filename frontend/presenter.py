# from interfaces import ILoginView, IPortfolioView, IAuthService, IPortfolioService
# from model import Portfolio
# from datetime import datetime
# from PySide6.QtWidgets import QMessageBox
# from interfaces import IPortfolioView, IPortfolioService
# from model import Portfolio


# class LoginPresenter:
#     def __init__(self, view: ILoginView, auth_service: IAuthService):
#         self.view = view
#         self.auth_service = auth_service

#         self.view.login_requested.connect(self.handle_login)
#         self.view.signup_requested.connect(self.handle_signup)
        


#     def handle_login(self, username: str, password: str):
#         """Handles login attempt and updates UI accordingly."""
#         if self.auth_service.authenticate(username, password):
#             self.view.clear_inputs()
#             self.view.login_successful.emit(self.auth_service.get_user_id())
#         else:
#             self.show_error("Invalid username or password")

#     def handle_signup(self, username: str, password: str):
#         """Handles user registration."""
#         if self.auth_service.register(username, password):
#             self.view.clear_inputs()
#             self.view.login_successful.emit(self.auth_service.get_user_id())
#         else:
#             self.show_error("Username already exists or failed to register.")

#     def show_error(self, message):
#         """Display error message in a popup."""
#         msg_box = QMessageBox()
#         msg_box.setIcon(QMessageBox.Critical)
#         msg_box.setWindowTitle("Login Failed")
#         msg_box.setText(message)
#         msg_box.exec()



# class PortfolioPresenter:
#     def __init__(self, view: IPortfolioView, portfolio_service: IPortfolioService, user_id: str):
#         self.view = view
#         self.service = portfolio_service
#         self.current_user_id = user_id  # ✅ Now real user!
#         self.view.stock_search_requested.connect(self.handle_stock_search)


#         # Connect UI signals to functions
#         self.view.buy_requested.connect(self.handle_buy)
#         self.view.sell_requested.connect(self.handle_sell)

#     def load_portfolio(self):
#         """Fetches portfolio data and updates the UI."""
#         print("Loading portfolio for user:", self.current_user_id)
#         portfolio = self.service.get_portfolio(self.current_user_id)
#         print("Portfolio total value:", portfolio.total_value)
#         print("Stocks in portfolio:", [f"{s.symbol} ({s.shares})" for s in portfolio.stocks])
        

#         self.view.set_username(portfolio.user.username)
#         profile_titles = [
#             "The Default", "Risk Taker", "Business Savvy", "The Analyst",
#             "Growth Guru", "Steady Saver", "Market Hawk", "The Bull", "The Bear"
#         ]

#         # Derive index from image URL
#         profile_index = 0  # fallback
#         url = portfolio.user.profileImageUrl or ""
#         if "profile_" in url:
#             try:
#                 name = url.split("profile_")[1].split(".")[0]
#                 profile_index = 0 if name == "default" else int(name)
#             except:
#                 profile_index = 0

#         self.view.set_profile_title(profile_titles[profile_index])

#         self.view.update_portfolio_summary(
#             portfolio.total_value,
#             self._calculate_daily_change(portfolio)
#         )
#         total_gain = sum(stock.gain_loss for stock in portfolio.stocks)
#         self.view.update_total_gain_loss(total_gain)
#         self.view.update_holdings_table(portfolio.stocks)
#         self.view.update_transaction_history(portfolio.transactions)


#     def _calculate_daily_change(self, portfolio: Portfolio) -> float:
#         """Mock function to simulate daily change percentage."""
#         return 2.5  # Static value for now

#     def handle_buy(self, symbol: str, shares: int):
#         """Handles buy transactions."""
#         if self.service.execute_buy_order(self.current_user_id, symbol, shares):
#             self.load_portfolio()  # Refresh UI after transaction
#         else:
#             self.view.show_error("Failed to execute buy order")

#     def handle_sell(self, symbol: str, shares: int):
#         """Handles sell transactions."""
#         if self.service.execute_sell_order(self.current_user_id, symbol, shares):
#             self.load_portfolio()  # Refresh UI after transaction
#         else:
#             self.view.show_error("Failed to execute sell order")

#     def handle_stock_search(self, symbol: str, period: str):
#         try:
#             history, name, price = self.service.get_stock_data(symbol, period)
#             self.view.update_stock_search_result(name, price, history)
#         except Exception as e:
#             print("Stock search failed:", e)
#             self.view.update_stock_search_result("Error", 0.0, [])

# from PySide6.QtCore import QObject, QTimer
# from services import ApiClient  # Your ApiClient
# from interfaces import IAiChatView  # Make sure this interface exists

# class AiChatPresenter(QObject):
#     def __init__(self, view: IAiChatView, api_client: ApiClient, user_id: str):
#         super().__init__()
#         self.view = view
#         self.api_client = api_client
#         self.user_id = user_id

#         # Connect the view's send_message signal to our handler
#         self.view.send_message_requested.connect(self.handle_send_message)

#     def handle_send_message(self, message: str):
#         if not message.strip():
#             return

#         # Immediately show user message in chat
#         self.view.add_message(message)

#         # Show typing indicator
#         self.view.set_typing_indicator(True)

#         # Fetch AI response (simulate slight delay for UX)
#         QTimer.singleShot(300, lambda: self.fetch_ai_answer(message))

#     def fetch_ai_answer(self, question: str):
#         try:
#             # Ask the AI via API client
#             response = self.api_client.ask(question)
            
#             # Display the AI's response
#             self.view.add_message(response)

#         except Exception as e:
#             error_message = f"Failed to get AI response: {str(e)}"
#             self.view.add_message(error_message)

#         finally:
#             # Hide typing indicator
#             self.view.set_typing_indicator(False)

    
from interfaces import ILoginView, IPortfolioView, IAuthService, IPortfolioService
from model import Portfolio
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from interfaces import IPortfolioView, IPortfolioService
from model import Portfolio
from PySide6.QtCore import QObject, QThread, Signal
from services import ApiClient
from interfaces import IAiChatView

class LoginPresenter:
    def __init__(self, view: ILoginView, auth_service: IAuthService):
        self.view = view
        self.auth_service = auth_service

        self.view.login_requested.connect(self.handle_login)
        self.view.signup_requested.connect(self.handle_signup)

    def handle_login(self, username: str, password: str):
        if self.auth_service.authenticate(username, password):
            self.view.clear_inputs()
            self.view.login_successful.emit(self.auth_service.get_user_id())
        else:
            self.show_error("Invalid username or password")

    def handle_signup(self, username: str, password: str):
        if self.auth_service.register(username, password):
            self.view.clear_inputs()
            self.view.login_successful.emit(self.auth_service.get_user_id())
        else:
            self.show_error("Username already exists or failed to register.")

    def show_error(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Login Failed")
        msg_box.setText(message)
        msg_box.exec()


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


class AiWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, service, message, user_id):
        super().__init__()
        self.service = service
        self.message = message
        self.user_id = user_id

    def run(self):
        try:
            answer = self.service.ask(self.message)
            self.finished.emit(answer)
        except Exception as e:
            self.error.emit(str(e))


class AiChatPresenter(QObject):
    def __init__(self, view: IAiChatView, api_client: ApiClient, user_id: str):
        super().__init__()
        self.view = view
        self.service = api_client
        self.user_id = user_id

        self.view.send_message_requested.connect(self.handle_send_message)

    def handle_send_message(self, message: str):
        if not message.strip():
            return

        self.view.add_message(message)
        self.view.set_typing_indicator(True)

        self.worker = AiWorker(self.service, message, self.user_id)
        self.thread = QThread()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.error.connect(self.handle_ai_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_ai_response(self, response: str):
        self.view.set_typing_indicator(False)
        self.view.add_message(response)

    def handle_ai_error(self, error_message: str):
        self.view.set_typing_indicator(False)
        self.view.add_message(f"Error: {error_message}")
