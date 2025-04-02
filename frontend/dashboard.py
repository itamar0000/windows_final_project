from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QFrame, QGridLayout, 
                             QHeaderView, QStackedWidget)
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from typing import List, Optional
from datetime import datetime
from services import StockService
from model import Stock, Portfolio
from interfaces import ILoginView, IPortfolioView, IStockService
import sys
from PySide6.QtGui import QPixmap
import requests
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog
import os
from api_client import ApiClient



class StyleSheet:
    MAIN_STYLE = """
    QMainWindow {
        background-color: #f5f6fa;
    }
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QLabel {
        color: #2c3e50;
        font-size: 14px;
    }
    QLineEdit {
        padding: 8px;
        border: 2px solid #dcdde1;
        border-radius: 4px;
        background-color: white;
        font-size: 14px;
        color: #2c3e50;
    }
    QPushButton {
        background-color: #3498db;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        font-size: 14px;
        font-weight: bold;
    }
    QTableWidget{
        background-color: white;
        border: 1px solid #dcdde1;
        color: #2c3e50;
    }
    """

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

class LoginView(QWidget):
    login_requested = Signal(str, str)
    signup_requested = Signal(str, str)    
    forgot_password_requested = Signal(str)
    login_successful = Signal(str)  # pass userId to Portfolio
    

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Title
        title = QLabel("Stock Portfolio Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")

        # Username Field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(self._input_style())

        # Password Field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self._input_style())

        # Login Button
        login_button = QPushButton("Login")
        login_button.setStyleSheet(self._button_style())
        login_button.clicked.connect(self._handle_login_click)

        # Sign Up Button
        signup_button = QPushButton("Sign Up")
        signup_button.setStyleSheet(self._button_style())
        signup_button.clicked.connect(self._handle_signup_click)


        # Forgot Password
        self.forgot_password_label = QLabel("<a href='#'>Forgot Password?</a>")
        self.forgot_password_label.setStyleSheet("font-size: 12px; color: #3498db;")
        self.forgot_password_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.forgot_password_label.setOpenExternalLinks(False)
        self.forgot_password_label.linkActivated.connect(self._handle_forgot_password)

        # Add Widgets to Layout
        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(signup_button)

        layout.addWidget(self.forgot_password_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _input_style(self):
        return """
        QLineEdit {
            padding: 10px;
            border: 2px solid #dcdde1;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
            color: #2c3e50;
        }
        """

    def _button_style(self):
        return """
        QPushButton {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        """

    def clear_inputs(self):
        """Clears the username and password fields after login."""
        self.username_input.clear()
        self.password_input.clear()

    def _handle_login_click(self):
        """Emits login request signal with username and password."""
        username, password = self.username_input.text(), self.password_input.text()
        self.login_requested.emit(username, password)
        

    def _handle_signup_click(self):
        username, password = self.username_input.text(), self.password_input.text()
        self.signup_requested.emit(username, password)


    def _handle_forgot_password(self):
        """Emits forgot password request signal."""
        self.forgot_password_requested.emit(self.username_input.text())




class PortfolioView(QWidget):
    buy_requested = Signal(str, int)
    sell_requested = Signal(str, int)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()
        layout.setSpacing(30    )
        layout.setContentsMargins(50, 50, 50, 50)

        self.summary_card = self._create_summary_card()
        self.holdings_table = self._create_holdings_table()
        self.chart_view = self._create_performance_chart()
        self.trading_card = self._create_trading_card()

        layout.addWidget(self.summary_card, 0, 0, 1, 2)
        layout.addWidget(self.holdings_table, 1, 0, 1, 1)
        layout.addWidget(self.chart_view, 1, 1, 1, 1)
        layout.addWidget(self.trading_card, 2, 0, 1, 2)

        self.setLayout(layout)

    def _create_summary_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border:1px solid black; padding: 15px; }")

        layout = QHBoxLayout()

        # 🖼 Profile Picture
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(100, 100)
        self.profile_pic_label.setStyleSheet("border: 1px solid #ccc;")
        self.profile_pic_label.setAlignment(Qt.AlignCenter)

        # Load default image (local asset)
        default_path = os.path.join(os.path.dirname(__file__), "assets/default_profile.png")
        default_pixmap = QPixmap(default_path)

        self.profile_pic_label.setPixmap(default_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 📤 Upload Button
        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self._handle_upload_image)

        # Left section (image + button)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.profile_pic_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)

        # Portfolio summary
        summary_layout = QVBoxLayout()
        self.total_value_label = QLabel("$0.00")
        self.total_value_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.daily_change_label = QLabel("$0.00 (0.00%)")
        self.daily_change_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        summary_layout.addWidget(self.total_value_label)
        summary_layout.addWidget(self.daily_change_label)

        layout.addLayout(left_layout)
        layout.addLayout(summary_layout)
        card.setLayout(layout)

        return card

    def _create_holdings_table(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; color:black}")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Stock Holdings"))
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(4)
        self.stock_table.setStyleSheet("""
    QHeaderView::section {
        background-color: #f0f0f0;
        padding: 4px;
        border: 1px solid #d0d0d0;
        color: #2c3e50;
    }
""")
        self.stock_table.setHorizontalHeaderLabels(["Symbol", "Shares", "Price", "Value"])
        self.stock_table.verticalHeader().setVisible(True)
        self.stock_table.horizontalHeader().setMinimumHeight(70)
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.stock_table)
        card.setLayout(layout)
        
        return card

    def _create_performance_chart(self) -> QChartView:
        chart = QChart()
        chart.setTheme(QChart.ChartThemeLight)
        
        self.performance_series = QLineSeries()
        chart.addSeries(self.performance_series)
        chart.createDefaultAxes()
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view

    def _create_trading_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 8px; padding: 15px; }")
        
        layout = QHBoxLayout()
        
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Stock Symbol")
        
        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("Number of Shares")
        
        buy_button = QPushButton("Buy")
        buy_button.clicked.connect(self._handle_buy)
        
        sell_button = QPushButton("Sell")
        sell_button.clicked.connect(self._handle_sell)
        
        layout.addWidget(self.symbol_input)
        layout.addWidget(self.shares_input)
        layout.addWidget(buy_button)
        layout.addWidget(sell_button)
        
        card.setLayout(layout)
        return card

    def update_portfolio_summary(self, total_value: float, daily_change: float):
        self.total_value_label.setText(f"${total_value:,.2f}")
        
        change_color = "#27ae60" if daily_change >= 0 else "#e74c3c"
        self.daily_change_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {change_color};")
        self.daily_change_label.setText(f"${abs(daily_change):,.2f} ({daily_change:+.2f}%)")

    def update_holdings_table(self, holdings: List[Stock]):
        self.stock_table.setRowCount(len(holdings))
        
        for row, stock in enumerate(holdings):
            self.stock_table.setItem(row, 0, QTableWidgetItem(stock.symbol))
            self.stock_table.setItem(row, 1, QTableWidgetItem(str(stock.shares)))
            self.stock_table.setItem(row, 2, QTableWidgetItem(f"${stock.current_price:,.2f}"))
            self.stock_table.setItem(row, 3, QTableWidgetItem(f"${stock.value:,.2f}"))

    def update_performance_chart(self, data: List[tuple[datetime, float]]):
        self.performance_series.clear()
        for date, value in data:
            self.performance_series.append(date.timestamp(), value)

    def show_error(self, message: str):
        # TODO: Implement error display (could use a QMessageBox or status bar)
        print(f"Error: {message}")

    def _handle_buy(self):
        try:
            symbol = self.symbol_input.text().upper()
            shares = int(self.shares_input.text())
            self.buy_requested.emit(symbol, shares)
            self.symbol_input.clear()
            self.shares_input.clear()
        except ValueError:
            self.show_error("Invalid number of shares")

    def _handle_sell(self):
        try:
            symbol = self.symbol_input.text().upper()
            shares = int(self.shares_input.text())
            self.sell_requested.emit(symbol, shares)
            self.symbol_input.clear()
            self.shares_input.clear()
        except ValueError:
            self.show_error("Invalid number of shares")
    def _handle_upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            print("Selected image:", file_path)
        # We'll call MainWindow or the Presenter to do the actual upload later



class StockSearchView(QWidget):
    stock_selected = Signal(str)  # Emits symbol when stock is selected

    def __init__(self, stock_service: IStockService):
        super().__init__()
        self.stock_service = stock_service
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search stocks (e.g., AAPL, Apple)")
        self.search_input.textChanged.connect(self._handle_search)
        
        search_layout.addWidget(self.search_input)
        
        # Results list
        self.results_list = QTableWidget()
        self.results_list.setColumnCount(2)
        self.results_list.setHorizontalHeaderLabels(["Symbol", "Company"])
        self.results_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_list.itemClicked.connect(self._handle_selection)
        
        # Stock info section
        self.info_layout = QVBoxLayout()
        self.company_name = QLabel()
        self.current_price = QLabel()
        self.company_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.current_price.setStyleSheet("font-size: 16px;")
        
        # Chart
        self.chart_view = self._create_stock_chart()
        
        # Add all to main layout
        layout.addLayout(search_layout)
        layout.addWidget(self.results_list)
        layout.addWidget(self.company_name)
        layout.addWidget(self.current_price)
        layout.addWidget(self.chart_view)
        
        self.setLayout(layout)

    def _create_stock_chart(self) -> QChartView:
        chart = QChart()
        chart.setTheme(QChart.ChartThemeLight)
        
        self.stock_series = QLineSeries()
        chart.addSeries(self.stock_series)
        chart.createDefaultAxes()
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view

    def _handle_search(self):
        query = self.search_input.text()
        if len(query) >= 2:  # Only search if at least 2 characters
            results = self.stock_service.search_stock(query)
            self.results_list.setRowCount(len(results))
            
            for row, (symbol, name) in enumerate(results):
                self.results_list.setItem(row, 0, QTableWidgetItem(symbol))
                self.results_list.setItem(row, 1, QTableWidgetItem(name))

    def _handle_selection(self, item):
        symbol = self.results_list.item(item.row(), 0).text()
        self.stock_selected.emit(symbol)
        self._load_stock_data(symbol)

    def _load_stock_data(self, symbol: str):
        history, name, price = self.stock_service.get_stock_data(symbol)
        
        # Update info
        self.company_name.setText(name)
        self.current_price.setText(f"${price:,.2f}")
        
        # Update chart
        self.stock_series.clear()
        for date, value in history:
            self.stock_series.append(date.timestamp(), value)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = ApiClient("http://localhost:5000")
        self.setWindowTitle("Stock Portfolio Manager")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(StyleSheet.MAIN_STYLE)

        self.stack = QStackedWidget()
        
        self.login_view = LoginView()
        self.portfolio_view = PortfolioView()
        self.stock_search_view = StockSearchView(StockService())  # Add this line
        
        # Connect signals
        self.login_view.login_successful.connect(self.show_portfolio)
        
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.portfolio_view)
        self.stack.addWidget(self.stock_search_view)  # Add this line
        
        self.setCentralWidget(self.stack)
        
        # Add navigation menu
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu('View')
        
        portfolio_action = view_menu.addAction('Portfolio')
        portfolio_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.portfolio_view))
        
        search_action = view_menu.addAction('Stock Search')
        search_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.stock_search_view))
        
    def show_portfolio(self, user_id: str):
        self.stack.setCurrentWidget(self.portfolio_view)
        self.load_user_profile_image(user_id)


    def load_user_profile_image(self, user_id: str):
        image_url = self.api.get_profile_image(user_id)
        if image_url:
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    self.portfolio_view.profile_pic_label.setPixmap(
                        pixmap.scaled(
                            self.portfolio_view.profile_pic_label.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                    )
                else:
                    self.portfolio_view.profile_pic_label.setText("Image error")
            except Exception as e:
                print("Image fetch failed:", e)
                self.portfolio_view.profile_pic_label.setText("Image error")
        else:
            self.portfolio_view.profile_pic_label.setText("No Image")