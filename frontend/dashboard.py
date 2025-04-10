from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QGridLayout, 
    QHeaderView, QStackedWidget, QTabWidget, QToolBar  # Add QToolBar here
)
from PySide6.QtGui import QAction  # Add this import for QAction
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt, Signal, QSize, QPointF
from PySide6.QtGui import QColor, QPainter, QFont, QPixmap, QIcon
from typing import List, Optional
from datetime import datetime
import requests
import sys
import os

from services import StockService
from api_client import ApiClient
from model import Stock, Portfolio
from interfaces import ILoginView, IPortfolioView, IStockService




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
    upload_image_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Top section with profile and portfolio value
        self.header_section = self._create_header_section()
        main_layout.addWidget(self.header_section)
        
        # Central content area
        central_container = QTabWidget()
        central_container.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                border-radius: 8px;
                background-color: white;
            }
            QTabWidget::tab-bar {
                left: 10px;
            }
            QTabBar::tab {
                background-color: #f5f6fa;
                color: #2c3e50;
                border: 1px solid #dcdde1;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        # Holdings tab
        holdings_widget = self._create_holdings_tab()
        central_container.addTab(holdings_widget, "My Portfolio")
        
        # Transactions tab
        transactions_widget = self._create_transactions_tab()
        central_container.addTab(transactions_widget, "Transaction History")
        
        # Add central content to the main layout
        main_layout.addWidget(central_container, 1)
        
        # Bottom section with trading controls
        self.trading_card = self._create_trading_card()
        main_layout.addWidget(self.trading_card)
        
        self.setLayout(main_layout)
        
        # Apply global styling
        self._apply_styles()

    def _create_header_section(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                color: white;
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Left side - Profile section
        profile_layout = QHBoxLayout()
        
        # Profile picture
        self.profile_pic_frame = QFrame()
        self.profile_pic_frame.setFixedSize(100, 100)
        self.profile_pic_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 50px;
                border: 3px solid white;
            }
        """)
        
        profile_pic_layout = QVBoxLayout()
        profile_pic_layout.setContentsMargins(0, 0, 0, 0)
        
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(94, 94)
        self.profile_pic_label.setStyleSheet("border-radius: 47px;")
        self.profile_pic_label.setScaledContents(True)
        
        # Set default profile image
        default_path = os.path.join(os.path.dirname(__file__), "assets/default_profile.png")
        default_pixmap = QPixmap(default_path)
        self.profile_pic_label.setPixmap(default_pixmap.scaled(94, 94, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        profile_pic_layout.addWidget(self.profile_pic_label, alignment=Qt.AlignCenter)
        self.profile_pic_frame.setLayout(profile_pic_layout)
        
        # Username and upload button
        user_details = QVBoxLayout()
        user_details.setSpacing(10)
        
        self.username_label = QLabel("Username")
        self.username_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.upload_button = QPushButton("Change Photo")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.upload_button.clicked.connect(lambda: self.upload_image_requested.emit())
        
        user_details.addWidget(self.username_label)
        user_details.addWidget(self.upload_button)
        
        profile_layout.addWidget(self.profile_pic_frame)
        profile_layout.addLayout(user_details)
        profile_layout.addStretch()
        
        # Right side - Portfolio value
        value_layout = QVBoxLayout()
        value_layout.setAlignment(Qt.AlignRight)
        
        portfolio_label = QLabel("PORTFOLIO VALUE")
        portfolio_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        
        self.total_value_label = QLabel("$0.00")
        self.total_value_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        
        self.daily_change_label = QLabel("$0.00 (0.00%)")
        self.daily_change_label.setStyleSheet("font-size: 18px;")
        
        value_layout.addWidget(portfolio_label, alignment=Qt.AlignRight)
        value_layout.addWidget(self.total_value_label, alignment=Qt.AlignRight)
        value_layout.addWidget(self.daily_change_label, alignment=Qt.AlignRight)
        
        # Add both sections to the header
        layout.addLayout(profile_layout, 1)
        layout.addLayout(value_layout, 1)
        
        header.setLayout(layout)
        return header

    def _create_holdings_tab(self) -> QWidget:
        holdings_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Holdings table
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title for the table
        title_layout = QHBoxLayout()
        holdings_title = QLabel("Your Stock Holdings")
        holdings_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        
        title_layout.addWidget(holdings_title)
        title_layout.addStretch()
        
        # Create table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(4)
        self.stock_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #dcdde1;
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 15px;
                border-bottom: 1px solid #ecf0f1;
            }
        """)
        self.stock_table.setHorizontalHeaderLabels(["Symbol", "Shares", "Price", "Value"])
        self.stock_table.verticalHeader().setVisible(False)
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        table_layout.addLayout(title_layout)
        table_layout.addWidget(self.stock_table)
        
        table_container.setLayout(table_layout)
        layout.addWidget(table_container)
        
        # Add performance chart
        chart_container = QFrame()
        chart_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                margin-top: 20px;
            }
        """)
        
        chart_layout = QVBoxLayout()
        
        chart_title = QLabel("Portfolio Performance")
        chart_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        # Create chart
        chart = QChart()
        chart.setTheme(QChart.ChartThemeLight)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("")
        chart.legend().setVisible(False)
        
        self.performance_series = QLineSeries()
        self.performance_series.setColor(QColor("#3498db"))
        chart.addSeries(self.performance_series)
        chart.createDefaultAxes()
        
        self.chart_view = QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(250)
        
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.chart_view)
        
        chart_container.setLayout(chart_layout)
        layout.addWidget(chart_container)
        
        holdings_widget.setLayout(layout)
        return holdings_widget

    def _create_transactions_tab(self) -> QWidget:
        transactions_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Transactions table
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        transactions_title = QLabel("Recent Transactions")
        transactions_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        # Create table
        self.transaction_list = QTableWidget()
        self.transaction_list.setColumnCount(4)
        self.transaction_list.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #dcdde1;
                color: #2c3e50;
                font-weight: bold;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 15px;
                border-bottom: 1px solid #ecf0f1;
            }
        """)
        self.transaction_list.setHorizontalHeaderLabels(["Action", "Symbol", "Shares", "Price"])
        self.transaction_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_list.verticalHeader().setVisible(False)
        self.transaction_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.transaction_list.setEditTriggers(QTableWidget.NoEditTriggers)
        
        table_layout.addWidget(transactions_title)
        table_layout.addWidget(self.transaction_list)
        
        table_container.setLayout(table_layout)
        layout.addWidget(table_container)
        
        transactions_widget.setLayout(layout)
        return transactions_widget

    def _create_trading_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        trading_title = QLabel("Trade Stocks")
        trading_title.setStyleSheet("font-size: 18px; color: #2c3e50;")
        
        # Trading form
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)
        
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Stock Symbol (e.g., AAPL)")
        self.symbol_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                background-color: #f5f6fa;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("Number of Shares")
        self.shares_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                background-color: #f5f6fa;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        buy_button = QPushButton("Buy")
        buy_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        buy_button.clicked.connect(self._handle_buy)
        
        sell_button = QPushButton("Sell")
        sell_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        sell_button.clicked.connect(self._handle_sell)
        
        form_layout.addWidget(self.symbol_input, 2)
        form_layout.addWidget(self.shares_input, 1)
        form_layout.addWidget(buy_button)
        form_layout.addWidget(sell_button)
        
        layout.addWidget(trading_title)
        layout.addLayout(form_layout)
        
        card.setLayout(layout)
        return card

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f5f6fa;
            }
        """)

    def set_username(self, username: str):
        self.username_label.setText(username)

    def update_portfolio_summary(self, total_value: float, daily_change: float):
        self.total_value_label.setText(f"${total_value:,.2f}")

        change_color = "#27ae60" if daily_change >= 0 else "#e74c3c"
        self.daily_change_label.setStyleSheet(f"font-size: 18px; color: {change_color};")
        self.daily_change_label.setText(f"${abs(daily_change):,.2f} ({daily_change:+.2f}%)")

    def update_holdings_table(self, holdings: List):
        self.stock_table.setRowCount(len(holdings))

        for row, stock in enumerate(holdings):
            symbol_item = QTableWidgetItem(stock.symbol)
            symbol_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            
            shares_item = QTableWidgetItem(str(stock.shares))
            price_item = QTableWidgetItem(f"${stock.current_price:,.2f}")
            value_item = QTableWidgetItem(f"${stock.value:,.2f}")
            
            self.stock_table.setItem(row, 0, symbol_item)
            self.stock_table.setItem(row, 1, shares_item)
            self.stock_table.setItem(row, 2, price_item)
            self.stock_table.setItem(row, 3, value_item)

    def update_transaction_history(self, transactions: List):
        self.transaction_list.setRowCount(len(transactions))

        for row, tx in enumerate(transactions):
            action_item = QTableWidgetItem(tx.action_type.capitalize())
            symbol_item = QTableWidgetItem(tx.symbol)
            shares_item = QTableWidgetItem(str(tx.shares))
            price_item = QTableWidgetItem(f"${tx.price:.2f}")
            
            color = QColor("#27ae60") if tx.action_type.lower() == "buy" else QColor("#e74c3c")
            
            action_item.setForeground(color)
            symbol_item.setForeground(color)
            shares_item.setForeground(color)
            price_item.setForeground(color)
            
            self.transaction_list.setItem(row, 0, action_item)
            self.transaction_list.setItem(row, 1, symbol_item)
            self.transaction_list.setItem(row, 2, shares_item)
            self.transaction_list.setItem(row, 3, price_item)

    def update_performance_chart(self, data: List[tuple[datetime, float]]):
        self.performance_series.clear()
        for date, value in data:
            self.performance_series.append(date.timestamp() * 1000, value)

    def update_profile_image(self, image_url: str):
        try:
            import requests
            response = requests.get(image_url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                
                # Create circular mask for the profile picture
                self.profile_pic_label.setPixmap(
                    pixmap.scaled(
                        self.profile_pic_label.width(),
                        self.profile_pic_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            else:
                self.show_error("Failed to load updated image.")
        except Exception as e:
            print("Image load error:", e)
            self.show_error("Error loading image.")

    def show_error(self, message: str):
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


# You would also need to update the LoginView to match the new design style
class LoginView(QWidget):
    login_requested = Signal(str, str)
    signup_requested = Signal(str, str)    
    forgot_password_requested = Signal(str)
    login_successful = Signal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for login form
        login_container = QFrame()
        login_container.setFixedWidth(400)
        login_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dcdde1;
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)
        
        # Title
        title = QLabel("Stock Portfolio Manager")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        
        # Username Field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                background-color: #f5f6fa;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Password Field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                background-color: #f5f6fa;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Login Button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        login_button.clicked.connect(self._handle_login_click)
        
        # Sign Up Button
        signup_button = QPushButton("Sign Up")
        signup_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f6fa;
                color: #3498db;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #3498db;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        signup_button.clicked.connect(self._handle_signup_click)
        
        # Forgot Password
        self.forgot_password_label = QLabel("<a href='#'>Forgot Password?</a>")
        self.forgot_password_label.setStyleSheet("font-size: 14px; color: #3498db;")
        self.forgot_password_label.setAlignment(Qt.AlignCenter)
        self.forgot_password_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.forgot_password_label.setOpenExternalLinks(False)
        self.forgot_password_label.linkActivated.connect(self._handle_forgot_password)
        
        # Add Widgets to Layout
        form_layout.addWidget(title, alignment=Qt.AlignCenter)
        
        username_layout = QVBoxLayout()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)
        
        password_layout = QVBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        form_layout.addWidget(login_button)
        form_layout.addWidget(signup_button)
        form_layout.addWidget(self.forgot_password_label, alignment=Qt.AlignCenter)
        
        login_container.setLayout(form_layout)
        
        # Add container to main layout
        layout.addWidget(login_container, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #f5f6fa;")

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
        self.setup_ui()
        self.setup_toolbar()
        self.connect_signals()
        self.current_user_id = None

    def setup_ui(self):
        self.setWindowTitle("Stock Portfolio Manager")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
        """)
        
        self.stack = QStackedWidget()
        self.login_view = LoginView()
        self.portfolio_view = PortfolioView()
        
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.portfolio_view)
        
        self.setCentralWidget(self.stack)
        
        # Start with login view
        self.stack.setCurrentWidget(self.login_view)

    def setup_toolbar(self):
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QIcon().actualSize(QSize(24, 24)))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2c3e50;
                spacing: 10px;
                padding: 5px;
            }
            QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #34495e;
            }
            QToolButton:checked {
                background-color: #3498db;
            }
        """)
        
        # Create actions for toolbar
        portfolio_action = QAction("Portfolio", self)
        portfolio_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.portfolio_view))
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.handle_logout)
        
        # Add actions to toolbar
        self.toolbar.addAction(portfolio_action)
        self.toolbar.addAction(logout_action)
        
        # Initially hide toolbar until login
        self.toolbar.setVisible(False)
        self.addToolBar(self.toolbar)

    def connect_signals(self):
        self.login_view.login_successful.connect(self.show_portfolio)
        self.portfolio_view.upload_image_requested.connect(self.handle_image_upload)

    def show_portfolio(self, user_id: str):
        self.current_user_id = user_id
        self.stack.setCurrentWidget(self.portfolio_view)
        self.load_user_profile_image(user_id)
        self.toolbar.setVisible(True)

    def handle_logout(self):
        self.current_user_id = None
        self.login_view.clear_inputs()
        self.stack.setCurrentWidget(self.login_view)
        self.toolbar.setVisible(False)

    def load_user_profile_image(self, user_id: str):
        try:
            response = requests.get(f"http://localhost:5000/api/Image/profile-image/{user_id}")
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
                print("No profile image found, loading default.")
                self._set_default_profile_image()
        except Exception as e:
            print("Failed to fetch profile image:", e)
            self._set_default_profile_image()

    def _set_default_profile_image(self):
        default_url = "https://res.cloudinary.com/dxohlu5cy/image/upload/v1712060777/default/profile_default.png"
        try:
            response = requests.get(default_url)
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
            print("Default image fetch failed:", e)
            self.portfolio_view.profile_pic_label.setText("Image error")

    def handle_image_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path and self.current_user_id:
            print("Uploading:", file_path)
            url = self.api.upload_profile_image(self.current_user_id, file_path)
            if url:
                self.load_user_profile_image(self.current_user_id)
            else:
                QMessageBox.critical(self, "Upload Failed", "Failed to upload image.")