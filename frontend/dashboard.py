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
from model import Stock, Portfolio ,Transaction ,User
from interfaces import ILoginView, IPortfolioView, IStockService
from PySide6.QtWidgets import QFileDialog, QDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSizePolicy




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



from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QGridLayout, QStackedLayout, QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon, QPainter
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from typing import List
import requests
from model import Transaction

class PortfolioView(QWidget):
    buy_requested = Signal(str, int)
    sell_requested = Signal(str, int)
    upload_image_requested = Signal()
    change_profile_image_requested = Signal(int)
    stock_search_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        self.stacked_layout = QStackedLayout()

        self.section_portfolio = self.create_portfolio_section()
        self.section_transactions = self.create_transactions_section()
        self.section_performance = self.create_performance_section()
        self.section_search = self.create_stock_search_section()

        self.stacked_layout.addWidget(self.section_portfolio)
        self.stacked_layout.addWidget(self.section_transactions)
        self.stacked_layout.addWidget(self.section_performance)
        self.stacked_layout.addWidget(self.section_search)

        main_layout.addLayout(self.stacked_layout)
        self.setLayout(main_layout)

    def switch_section(self, index):
        self.stacked_layout.setCurrentIndex(index)

    def create_portfolio_section(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.username_label = QLabel("Username")
        self.profile_title_label = QLabel("")
        self.profile_title_label.setAlignment(Qt.AlignCenter)
        self.profile_title_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(self.profile_title_label)

        self.username_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.username_label)

        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(100, 100)
        self.profile_pic_label.setScaledContents(True)
        layout.addWidget(self.profile_pic_label, alignment=Qt.AlignCenter)

        change_btn = QPushButton("Change Profile Picture")
        change_btn.clicked.connect(self.show_image_selector)
        layout.addWidget(change_btn, alignment=Qt.AlignCenter)

        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_gain_loss_label = QLabel("Total Gain/Loss: $0.00")
        self.total_gain_loss_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_gain_loss_label)

        self.total_value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_value_label)

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels([
            "Symbol", "Shares", "Bought Price", "Current Price", "Value", "Gain/Loss"
        ])

        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.verticalHeader().setVisible(False)
        layout.addWidget(self.stock_table)

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Stock Symbol")
        layout.addWidget(self.symbol_input)

        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("Number of Shares")
        layout.addWidget(self.shares_input)

        buy_btn = QPushButton("Buy")
        buy_btn.clicked.connect(self._handle_buy)
        layout.addWidget(buy_btn)

        sell_btn = QPushButton("Sell")
        sell_btn.clicked.connect(self._handle_sell)
        layout.addWidget(sell_btn)

        widget.setLayout(layout)
        return widget

    def create_transactions_section(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(5)
        self.transaction_table.setHorizontalHeaderLabels(["Action", "Symbol", "Shares", "Price", "Date"])


        self.transaction_table.horizontalHeader().setStretchLastSection(True)
        self.transaction_table.verticalHeader().setVisible(False)
        layout.addWidget(self.transaction_table)

        widget.setLayout(layout)
        return widget

    def create_performance_section(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Performance chart placeholder"))
        widget.setLayout(layout)
        return widget

    def create_stock_search_section(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Stock Symbol")
        layout.addWidget(self.search_input)

        self.period_selector = QComboBox()
        self.period_selector.addItems(["1W", "1M", "3M", "6M", "1Y", "5Y", "10Y"])
        layout.addWidget(self.period_selector)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._handle_search_click)
        layout.addWidget(search_btn)

        self.search_info_label = QLabel("Symbol info will appear here")
        layout.addWidget(self.search_info_label)

        self.chart_view = QChartView(QChart())
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

        widget.setLayout(layout)
        return widget

    def _handle_search_click(self):
        symbol = self.search_input.text().strip().upper()
        period = self.period_selector.currentText()
        if symbol:
            self.stock_search_requested.emit(symbol, period)


    def update_stock_search_result(self, name: str, price: float, history: List[tuple]):
        self.search_info_label.setText(f"{name}: ${price:,.2f}")
        series = QLineSeries()
        for date, value in history:
            series.append(date.timestamp(), value)

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("Price History")
        self.chart_view.setChart(chart)


    def update_total_gain_loss(self, amount: float):
        color = "green" if amount > 0 else "red" if amount < 0 else "black"
        self.total_gain_loss_label.setText(f"<span style='color:{color}'>Total Gain/Loss: ${amount:,.2f}</span>")


    def set_username(self, username: str):
        self.username_label.setText(username)

    def update_profile_image(self, image_url: str):
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.profile_pic_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print("Image load error:", e)

    def update_portfolio_summary(self, total_value: float, daily_change: float):
        self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")

    def update_holdings_table(self, holdings):
        self.stock_table.setRowCount(len(holdings))
        for row, stock in enumerate(holdings):
            self.stock_table.setItem(row, 0, QTableWidgetItem(stock.symbol))
            self.stock_table.setItem(row, 1, QTableWidgetItem(str(stock.shares)))
            self.stock_table.setItem(row, 2, QTableWidgetItem(f"${stock.purchase_price:,.2f}"))
            self.stock_table.setItem(row, 3, QTableWidgetItem(f"${stock.current_price:,.2f}"))
            self.stock_table.setItem(row, 4, QTableWidgetItem(f"${stock.value:,.2f}"))

            gain_loss_item = QTableWidgetItem(f"${stock.gain_loss:,.2f}")
            gain_loss_item.setForeground(Qt.green if stock.gain_loss > 0 else Qt.red if stock.gain_loss < 0 else Qt.black)
            self.stock_table.setItem(row, 5, gain_loss_item)


    def update_transaction_history(self, transactions: List[Transaction]):
        self.transaction_table.setRowCount(len(transactions))
        for row, tx in enumerate(transactions):
            self.transaction_table.setItem(row, 0, QTableWidgetItem(tx.action_type))
            self.transaction_table.setItem(row, 1, QTableWidgetItem(tx.symbol))
            self.transaction_table.setItem(row, 2, QTableWidgetItem(str(tx.shares)))
            self.transaction_table.setItem(row, 3, QTableWidgetItem(f"${tx.price:,.2f}"))

            try:
                # Parse and format the date nicely
                dt = datetime.fromisoformat(tx.timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = tx.timestamp  # fallback
            self.transaction_table.setItem(row, 4, QTableWidgetItem(date_str))


    def show_image_selector(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Profile Image")
        layout = QGridLayout()

        for i in range(9):
            image_name = "profile_default" if i == 0 else f"profile_{i}"
            image_url = f"https://res.cloudinary.com/dxohlu5cy/image/upload/default/{image_name}.png"

            # Profile titles (edit as needed)
            profile_titles = [
                "The Default", "Risk Taker", "Business Savvy", "The Analyst",
                "Growth Guru", "Steady Saver", "Market Hawk", "The Bull", "The Bear"
            ]

            # Image
            button = QPushButton()
            button.setFixedSize(80, 80)
            pixmap = QPixmap()

            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    pixmap.loadFromData(response.content)
                    button.setIcon(QIcon(pixmap))
                    button.setIconSize(button.size())
            except:
                continue

            button.clicked.connect(lambda _, index=i: self.select_preset(dialog, index))

            # Add image and label together
            image_layout = QVBoxLayout()
            image_layout.setAlignment(Qt.AlignCenter)
            image_layout.addWidget(button)

            label = QLabel(profile_titles[i])
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 12px; color: #2c3e50;")
            image_layout.addWidget(label)

            # Wrap in a container widget
            container = QWidget()
            container.setLayout(image_layout)
            layout.addWidget(container, i // 3, i % 3)


        dialog.setLayout(layout)
        dialog.exec()

    def select_preset(self, dialog, index):
        dialog.done(0)
        self.change_profile_image_requested.emit(index)

    def set_profile_title(self, title: str):
        self.profile_title_label.setText(title)


    def _handle_buy(self):
        symbol = self.symbol_input.text().upper()
        try:
            shares = int(self.shares_input.text())
            self.buy_requested.emit(symbol, shares)
        except ValueError:
            print("Invalid number of shares")

    def _handle_sell(self):
        symbol = self.symbol_input.text().upper()
        try:
            shares = int(self.shares_input.text())
            self.sell_requested.emit(symbol, shares)
        except ValueError:
            print("Invalid number of shares")




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
        self.portfolio_view.change_profile_image_requested.connect(self.set_profile_preset)

    def setup_toolbar(self):
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

        # Actions
        portfolio_action = QAction("Portfolio", self)
        portfolio_action.triggered.connect(lambda: self.portfolio_view.switch_section(0))

        transactions_action = QAction("Transactions", self)
        transactions_action.triggered.connect(lambda: self.portfolio_view.switch_section(1))

        search_action = QAction("Search", self)
        search_action.triggered.connect(lambda: self.portfolio_view.switch_section(3))

        ai_chat_action = QAction("AI Chat", self)
        ai_chat_action.triggered.connect(self.open_ai_chat_dialog)


        # Add actions to toolbar
        self.toolbar.addAction(portfolio_action)
        self.toolbar.addAction(transactions_action)
        self.toolbar.addAction(search_action)
        self.toolbar.addAction(ai_chat_action)

        # Spacer to push logout to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.handle_logout)
        self.toolbar.addAction(logout_action)

        self.toolbar.setVisible(False)
        self.addToolBar(self.toolbar)


    def set_profile_preset(self, index: int):
        if self.current_user_id is None:
            return

        try:
            response = requests.post(
                f"http://localhost:5000/api/Image/set-preset",
                data={"userId": self.current_user_id, "presetIndex": index}
            )
            if response.status_code == 200:
                self.load_user_profile_image(self.current_user_id)

                # Set title based on index
                profile_titles = [
                    "The Default", "Risk Taker", "Business Savvy", "The Analyst",
                    "Growth Guru", "Steady Saver", "Market Hawk", "The Bull", "The Bear"
                ]
                self.portfolio_view.set_profile_title(profile_titles[index])
            else:
                print("Failed to set preset image.")
        except Exception as e:
            print("Preset error:", e)


    def connect_signals(self):
        self.login_view.login_successful.connect(self.show_portfolio)
        self.portfolio_view.upload_image_requested.connect(self.handle_image_upload)

    def show_portfolio(self, user_id: str):
        self.current_user_id = user_id
        self.stack.setCurrentWidget(self.portfolio_view)
        self.load_user_profile_image(user_id)
        self.toolbar.setVisible(True)
        self.portfolio_view.switch_section(0)  


    def handle_logout(self):
        self.current_user_id = None
        self.login_view.clear_inputs()
        self.stack.setCurrentWidget(self.login_view)
        self.toolbar.setVisible(False)

    def _handle_portfolio_action(self):
        self.stack.setCurrentWidget(self.portfolio_view)
        if hasattr(self, "portfolio_presenter"):
            self.portfolio_presenter.load_portfolio()

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
        default_url = ".com/dxohlu5cy/image/upload/v1712060777/default/profile_default.png"
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
        self.portfolio_view.show_image_selector()


    def open_ai_chat_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("AI Chat Assistant")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Message area
        self.chat_display = QLabel("🤖 How can I help you today?")
        self.chat_display.setWordWrap(True)
        self.chat_display.setStyleSheet("font-size: 14px; padding: 10px; background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 6px;")
        layout.addWidget(self.chat_display)

        # Input
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your question...")
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.handle_ai_message)
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def handle_ai_message(self):
        question = self.chat_input.text().strip()
        if not question:
            return

        # Simulate AI reply (you can later plug in real backend)
        response = f"🤖 You said: {question}"

        self.chat_display.setText(response)
        self.chat_input.clear()
