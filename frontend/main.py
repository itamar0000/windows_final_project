from PySide6.QtWidgets import QApplication
import sys
from dashboard import MainWindow
from services import AuthService, PortfolioService
from presenter import LoginPresenter, PortfolioPresenter

def main():
    app = QApplication(sys.argv)

    # Create mock authentication service
    auth_service = AuthService()

    # Create main window
    window = MainWindow()

    # Connect Login Presenter
    login_presenter = LoginPresenter(window.login_view, auth_service)
     # Create portfolio service and presenter
    portfolio_service = PortfolioService()
    portfolio_presenter = PortfolioPresenter(window.portfolio_view, portfolio_service)

    # Load portfolio data when app starts
    portfolio_presenter.load_portfolio()
    # Show the main window
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
