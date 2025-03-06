# main.py
from PySide6.QtWidgets import QApplication
import sys
from dashboard import MainWindow
from services import AuthService, PortfolioService
from presenter import LoginPresenter, PortfolioPresenter

def main():
    app = QApplication(sys.argv)
    
    # Create services
    auth_service = AuthService()
    portfolio_service = PortfolioService()
    
    # Create main window
    window = MainWindow()
    
    # Create presenters and connect them to views
    login_presenter = LoginPresenter(window.login_view, auth_service)
    portfolio_presenter = PortfolioPresenter(window.portfolio_view, portfolio_service)
    
    # Show the window
    window.show()
    
    # Load initial portfolio data
    portfolio_presenter.load_portfolio()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()