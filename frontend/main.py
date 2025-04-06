from PySide6.QtWidgets import QApplication
import sys
from dashboard import MainWindow
from services import AuthService, PortfolioService
from presenter import LoginPresenter, PortfolioPresenter

def main():
    app = QApplication(sys.argv)

    # Create main window and services
    window = MainWindow()
    auth_service = AuthService()
    portfolio_service = PortfolioService()

    # Create login presenter
    login_presenter = LoginPresenter(window.login_view, auth_service)

    # Connect login success to create portfolio presenter
    def on_login_success(user_id: str):
        portfolio_presenter = PortfolioPresenter(window.portfolio_view, portfolio_service, user_id)
        portfolio_presenter.load_portfolio()
        window.show_portfolio(user_id)



    window.login_view.login_successful.connect(on_login_success)

    # Show window
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
