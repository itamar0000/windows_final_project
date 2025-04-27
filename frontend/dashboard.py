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


from ai_chat_view import AiChatView
from presenter import AiChatPresenter
from services import AiAdvisorService
from services import StockService
from api_client import ApiClient
from model import Stock, Portfolio ,Transaction ,User
from PySide6.QtWidgets import QFileDialog, QDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QBrush



from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QDialog, QGridLayout, QStackedLayout, 
    QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit, 
    QComboBox, QFrame, QHeaderView, QSizePolicy, QScrollArea,
    QSpacerItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor, QFont
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from typing import List
import requests
from datetime import datetime
from model import Transaction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QDialog, QGridLayout, QStackedLayout, 
    QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit, 
    QComboBox, QFrame, QHeaderView, QSizePolicy, QScrollArea,
    QSpacerItem
    )
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QPen  # Add QPen import here
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from typing import List
import requests
from datetime import datetime
from model import Transaction
from datetime import datetime, timedelta  # Add the timedelta import
from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QProgressBar




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
        # Main layout that contains everything
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main container with dark background
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: #0C0D10;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        container_layout = QHBoxLayout(main_container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(5)
                
        # Create stacked layout for different sections
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the different sections
        self.section_portfolio = self.create_portfolio_section()
        self.section_transactions = self.create_transactions_section()
        self.section_performance = self.create_performance_section()
        self.section_search = self.create_stock_search_section()
        
        # Add sections to stacked layout
        self.stacked_layout.addWidget(self.section_portfolio)
        self.stacked_layout.addWidget(self.section_transactions)
        self.stacked_layout.addWidget(self.section_performance)
        self.stacked_layout.addWidget(self.section_search)
        
        # Add stacked layout to the container
        container_layout.addLayout(self.stacked_layout)
        
        # Add container to main layout
        main_layout.addWidget(main_container)
        self.setLayout(main_layout)

    def switch_section(self, index):
        self.stacked_layout.setCurrentIndex(index)

    def create_portfolio_section(self):
        # Main widget with no scrolling to reduce space wastage
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #0C0D10;")
        
        # Use a grid layout for better space utilization
        main_layout = QGridLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)
        
        # User info and summary combined in a compact top bar with gradient background
        top_bar = QFrame()
        top_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1D23, stop:1 #252A34);
                border-radius: 10px;
                border: 1px solid #2C313A;
            }
        """)
        top_bar.setMaximumHeight(90)
        
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 10, 15, 10)
        
        # User section (left side of top bar) with improved design
        user_section = QFrame()
        user_section.setStyleSheet("background: transparent;")
        user_layout = QHBoxLayout(user_section)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(12)
        
        # Profile picture with glow effect
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(60, 60)
        self.profile_pic_label.setScaledContents(True)
        self.profile_pic_label.setStyleSheet("""
            QLabel {
                border: 2px solid #F0B90B;
                border-radius: 30px;
                background-color: #2A2D35;
            }
        """)
        
        # User name and role with improved typography
        user_text = QVBoxLayout()
        user_text.setSpacing(3)
        
        self.username_label = QLabel("Username")
        self.username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        
        self.profile_title_label = QLabel("")
        self.profile_title_label.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        
        change_btn = QPushButton("Change Avatar")
        change_btn.setCursor(Qt.PointingHandCursor)
        change_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(240, 185, 11, 0.1);
                border: 1px solid #F0B90B;
                border-radius: 4px;
                color: #F0B90B;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(240, 185, 11, 0.2);
            }
        """)
        change_btn.setMaximumWidth(100)
        change_btn.clicked.connect(self.show_image_selector)
        
        user_text.addWidget(self.username_label)
        user_text.addWidget(self.profile_title_label)
        user_text.addWidget(change_btn)
        
        user_layout.addWidget(self.profile_pic_label)
        user_layout.addLayout(user_text)
        
        # Portfolio summary (middle of top bar) with improved visualization
        portfolio_summary = QFrame()
        portfolio_summary.setStyleSheet("background: transparent;")
        summary_layout = QVBoxLayout(portfolio_summary)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(5)
        
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_value_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        
        self.total_gain_loss_label = QLabel("Total Gain/Loss: $0.00")
        self.total_gain_loss_label.setStyleSheet("font-size: 14px; color: #F0B90B;")
        
        summary_layout.addWidget(self.total_value_label)
        summary_layout.addWidget(self.total_gain_loss_label)
        
        # Performance indicators (right side of top bar) - Improved card-based design
        performance_view = QFrame()
        performance_view.setStyleSheet("background: transparent;")
        performance_layout = QHBoxLayout(performance_view)
        performance_layout.setContentsMargins(0, 0, 0, 0)
        performance_layout.setSpacing(10)
        
        # Enhanced stats with animated hover effect
        stats = [
            {"title": "Day", "value": "+2.5%", "color": "#00C087", "trend": "up"},
            {"title": "Week", "value": "-1.2%", "color": "#F6465D", "trend": "down"},
            {"title": "Month", "value": "+8.7%", "color": "#00C087", "trend": "up"}
        ]
        
        for stat in stats:
            stat_frame = QFrame()
            
            # Different background color based on trend
            bg_color = "rgba(0, 192, 135, 0.1)" if stat["trend"] == "up" else "rgba(246, 70, 93, 0.1)"
            border_color = "#00C087" if stat["trend"] == "up" else "#F6465D"
            
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 4px;
                }}
                QFrame:hover {{
                    border: 1px solid {stat["color"]};
                    background-color: {bg_color.replace('0.1', '0.2')};
                }}
            """)
            
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setContentsMargins(8, 6, 8, 6)
            stat_layout.setSpacing(2)
            
            title = QLabel(stat["title"])
            title.setStyleSheet("font-size: 11px; color: #BBBBBB; font-weight: bold;")
            
            # Add trend icon
            icon = "▲" if stat["trend"] == "up" else "▼"
            value = QLabel(f"{icon} {stat['value']}")
            value.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {stat['color']};")
            
            stat_layout.addWidget(title)
            stat_layout.addWidget(value)
            
            performance_layout.addWidget(stat_frame)
        
        # Add all sections to top bar
        top_bar_layout.addWidget(user_section, 2)
        top_bar_layout.addWidget(portfolio_summary, 3)
        top_bar_layout.addWidget(performance_view, 2)
        
        # Holdings table section - EXPANDED and improved with modern styling
        holdings_section = QFrame()
        holdings_section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A1D23, stop:1 #1E2026);
                border-radius: 10px;
                border: 1px solid #2C313A;
            }
        """)
        
        holdings_layout = QVBoxLayout(holdings_section)
        holdings_layout.setContentsMargins(15, 15, 15, 15)
        holdings_layout.setSpacing(12)
        
        holdings_header = QHBoxLayout()
        
        holdings_title = QLabel("YOUR HOLDINGS")
        holdings_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F0B90B;")
        
        # Add real-time indicator with pulsing animation effect
        status_layout = QHBoxLayout()
        status_dot = QLabel("•")
        status_dot.setStyleSheet("""
            QLabel {
                color: #00C087;
                font-size: 24px;
                margin-right: -0px;
            }
        """)
        
        status_label = QLabel("Real-time updates")
        status_label.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)
        
        holdings_header.addWidget(holdings_title)
        holdings_header.addStretch()
        holdings_header.addLayout(status_layout)
        
        # Enhanced table with modern styling
        self.stock_table = QTableWidget()
        self.stock_table.setMinimumHeight(350)
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels([
            "Symbol", "Shares", "Bought Price", "Current Price", "Value", "Gain/Loss"
        ])
        self.stock_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: #2A2D35;
                color: white;
                font-size: 13px;
                selection-background-color: rgba(240, 185, 11, 0.2);
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #2A2D35;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #F0B90B;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2A2D35;
            }
            QTableWidget::item:hover {
                background-color: rgba(42, 45, 53, 0.5);
            }
        """)
        
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.verticalHeader().setVisible(False)
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setShowGrid(False)
        
        holdings_layout.addLayout(holdings_header)
        holdings_layout.addWidget(self.stock_table)
        
        # Add quick action buttons below table
        action_buttons = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon(":/icons/refresh.png"))  # You would need to add this icon
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34373F;
            }
        """)
        
        export_btn = QPushButton("Export")
        export_btn.setIcon(QIcon(":/icons/export.png"))  # You would need to add this icon
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34373F;
            }
        """)
        
        action_buttons.addWidget(refresh_btn)
        action_buttons.addWidget(export_btn)
        action_buttons.addStretch()
        
        holdings_layout.addLayout(action_buttons)
        
        # Redesigned trade form with improved user flow
        trade_form = QFrame()
        trade_form.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1D23, stop:1 #252A34);
                border-radius: 10px;
                border: 1px solid #2C313A;
            }
        """)
        
        trade_layout = QVBoxLayout(trade_form)
        trade_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add header with icon
        trade_header = QHBoxLayout()
        
        trade_title = QLabel("QUICK TRADE")
        trade_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F0B90B;")
        
        # Trading interface with more intuitive layout
        trade_form_layout = QHBoxLayout()
        trade_form_layout.setSpacing(15)
        
        # Symbol input with validation
        symbol_layout = QVBoxLayout()
        symbol_layout.setSpacing(5)
        
        symbol_label = QLabel("Symbol")
        symbol_label.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter stock symbol (e.g. AAPL)")
        self.symbol_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #2A2D35;
                border-radius: 6px;
                background-color: #2A2D35;
                color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        
        symbol_layout.addWidget(symbol_label)
        symbol_layout.addWidget(self.symbol_input)
        
        # Shares input with validation
        shares_layout = QVBoxLayout()
        shares_layout.setSpacing(5)
        
        shares_label = QLabel("Shares")
        shares_label.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        
        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("Enter quantity")
        self.shares_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #2A2D35;
                border-radius: 6px;
                background-color: #2A2D35;
                color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        
        shares_layout.addWidget(shares_label)
        shares_layout.addWidget(self.shares_input)
        
        # Button layout with improved visual hierarchy
        action_layout = QVBoxLayout()
        action_layout.setSpacing(5)
        
        action_label = QLabel("Action")
        action_label.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(10)
        
        buy_btn = QPushButton("BUY")
        buy_btn.setCursor(Qt.PointingHandCursor)
        buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #00C087;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #00D68F;
            }
        """)
        buy_btn.clicked.connect(self._handle_buy)
        
        sell_btn = QPushButton("SELL")
        sell_btn.setCursor(Qt.PointingHandCursor)
        sell_btn.setStyleSheet("""
            QPushButton {
                background-color: #F6465D;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #FF5D6F;
            }
        """)
        sell_btn.clicked.connect(self._handle_sell)
        
        buttons_container.addWidget(buy_btn)
        buttons_container.addWidget(sell_btn)
        
        action_layout.addWidget(action_label)
        action_layout.addLayout(buttons_container)
        
        trade_form_layout.addLayout(symbol_layout, 3)
        trade_form_layout.addLayout(shares_layout, 2)
        trade_form_layout.addLayout(action_layout, 2)
        
        # Add components to trade layout
        trade_layout.addWidget(trade_title)
        trade_layout.addSpacing(5)
        trade_layout.addLayout(trade_form_layout)
        
        # Add all components to the main grid layout
        main_layout.addWidget(top_bar, 0, 0, 1, 1)
        main_layout.addWidget(holdings_section, 1, 0, 3, 1)
        main_layout.addWidget(trade_form, 4, 0, 1, 1)
        
        # Set row stretches to prioritize the holdings table
        main_layout.setRowStretch(0, 1)  # Top bar
        main_layout.setRowStretch(1, 8)  # Holdings
        main_layout.setRowStretch(4, 2)  # Trade form
        
        return main_widget
    
    def update_transaction_history(self, transactions: List[Transaction]):
        """Update the transaction table with actual transaction data and calculate totals"""
        # Clear existing rows
        self.transaction_table.setRowCount(len(transactions))
        
        total_bought = 0.0
        total_sold = 0.0
        
        for row, tx in enumerate(transactions):
            # Action type with proper color
            action_item = QTableWidgetItem(tx.action_type)
            
            # Set action color based on type (green for buy, red for sell)
            action_color = QColor("#00C087") if tx.action_type.upper() == "BUY" else QColor("#F6465D")
            action_item.setForeground(action_color)
            action_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            # Symbol
            symbol_item = QTableWidgetItem(tx.symbol)
            symbol_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            # Shares
            shares_item = QTableWidgetItem(str(tx.shares))
            
            # Price with formatting
            price_str = f"${tx.price:,.2f}"
            price_item = QTableWidgetItem(price_str)
            
            # Calculate transaction amount
            amount = tx.shares * tx.price
            
            # Update totals
            if tx.action_type.upper() == "BUY":
                total_bought += amount
            elif tx.action_type.upper() == "SELL":
                total_sold += amount
            
            # Date
            try:
                # Parse and format the date nicely
                dt = datetime.fromisoformat(tx.timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = tx.timestamp  # fallback
            date_item = QTableWidgetItem(date_str)
            
            # Status (new column)
            status = "Completed"  # Default status
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#00C087"))  # Green for completed
            
            # Set items in the table
            self.transaction_table.setItem(row, 0, action_item)
            self.transaction_table.setItem(row, 1, symbol_item)
            self.transaction_table.setItem(row, 2, shares_item)
            self.transaction_table.setItem(row, 3, price_item)
            self.transaction_table.setItem(row, 4, date_item)
            self.transaction_table.setItem(row, 5, status_item)
        
        # Update summary statistics
        self.tx_count_label.setText(str(len(transactions)))
        self.bought_amount_label.setText(f"${total_bought:,.2f}")
        self.sold_amount_label.setText(f"${total_sold:,.2f}")
        
        # Update page label - assuming 10 items per page
        items_per_page = 10
        total_pages = max(1, (len(transactions) + items_per_page - 1) // items_per_page)
        self.page_label.setText(f"Page 1 of {total_pages}")

    def create_transactions_section(self):
        # Create a scrollable area with enhanced styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0C0D10;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1E2026;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #2A2D35;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #F0B90B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Main widget container
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Enhanced header section with gradient background
        header_section = QFrame()
        header_section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1D23, stop:1 #252A34);
                border-radius: 10px;
                border: 1px solid #2C313A;
            }
        """)
        
        header_layout = QVBoxLayout(header_section)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(10)
        
        # Title with icon
        title_layout = QHBoxLayout()
        
        title_icon = QLabel("📝")  # Transaction icon
        title_icon.setStyleSheet("font-size: 24px; margin-right: 10px;")
        
        title = QLabel("Transaction History")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # Add stats summary to header
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Transaction count
        count_frame = QFrame()
        count_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(42, 45, 53, 0.7);
                border-radius: 8px;
                border: 1px solid #3A3D45;
            }
        """)
        count_layout = QVBoxLayout(count_frame)
        count_layout.setContentsMargins(15, 10, 15, 10)
        
        self.tx_count_label = QLabel("0")
        self.tx_count_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.tx_count_label.setAlignment(Qt.AlignCenter)
        
        count_title = QLabel("Total Transactions")
        count_title.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        count_title.setAlignment(Qt.AlignCenter)
        
        count_layout.addWidget(self.tx_count_label)
        count_layout.addWidget(count_title)
        
        # Total bought
        bought_frame = QFrame()
        bought_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 192, 135, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(0, 192, 135, 0.3);
            }
        """)
        bought_layout = QVBoxLayout(bought_frame)
        bought_layout.setContentsMargins(15, 10, 15, 10)
        
        self.bought_amount_label = QLabel("$0.00")
        self.bought_amount_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00C087;")
        self.bought_amount_label.setAlignment(Qt.AlignCenter)
        
        bought_title = QLabel("Total Bought")
        bought_title.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        bought_title.setAlignment(Qt.AlignCenter)
        
        bought_layout.addWidget(self.bought_amount_label)
        bought_layout.addWidget(bought_title)
        
        # Total sold
        sold_frame = QFrame()
        sold_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(246, 70, 93, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(246, 70, 93, 0.3);
            }
        """)
        sold_layout = QVBoxLayout(sold_frame)
        sold_layout.setContentsMargins(15, 10, 15, 10)
        
        self.sold_amount_label = QLabel("$0.00")
        self.sold_amount_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #F6465D;")
        self.sold_amount_label.setAlignment(Qt.AlignCenter)
        
        sold_title = QLabel("Total Sold")
        sold_title.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        sold_title.setAlignment(Qt.AlignCenter)
        
        sold_layout.addWidget(self.sold_amount_label)
        sold_layout.addWidget(sold_title)
        
        stats_layout.addWidget(count_frame)
        stats_layout.addWidget(bought_frame)
        stats_layout.addWidget(sold_frame)
        
        # Subtitle text
        subtitle = QLabel("Track all your buying and selling activities across your portfolio")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #BBBBBB;
            margin-top: 5px;
        """)
        
        # Add all elements to header layout
        header_layout.addLayout(title_layout)
        header_layout.addWidget(subtitle)
        header_layout.addSpacing(10)
        header_layout.addLayout(stats_layout)
        
        # Enhanced transactions table section
        table_section = QFrame()
        table_section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A1D23, stop:1 #1E2026);
                border-radius: 10px;
                border: 1px solid #2C313A;
            }
        """)
        
        table_layout = QVBoxLayout(table_section)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)
        
        # Add filter and search controls
        filter_layout = QHBoxLayout()
        
        # Time period filter
        period_layout = QHBoxLayout()
        period_layout.setSpacing(10)
        
        period_label = QLabel("Period:")
        period_label.setStyleSheet("font-size: 13px; color: white;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["All Time", "This Month", "Last Month", "This Year", "Custom"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #2A2D35;
                border-radius: 5px;
                background-color: #2A2D35;
                color: white;
                font-size: 13px;
                min-width: 120px;
            }
            QComboBox:focus, QComboBox:hover {
                border-color: #F0B90B;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2D35;
                color: white;
                border: 1px solid #F0B90B;
                selection-background-color: #F0B90B;
                selection-color: black;
                padding: 5px;
            }
        """)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        
        # Transaction type filter
        type_layout = QHBoxLayout()
        type_layout.setSpacing(10)
        
        type_label = QLabel("Type:")
        type_label.setStyleSheet("font-size: 13px; color: white;")
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All", "Buy", "Sell"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #2A2D35;
                border-radius: 5px;
                background-color: #2A2D35;
                color: white;
                font-size: 13px;
                min-width: 100px;
            }
            QComboBox:focus, QComboBox:hover {
                border-color: #F0B90B;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2D35;
                color: white;
                border: 1px solid #F0B90B;
                selection-background-color: #F0B90B;
                selection-color: black;
                padding: 5px;
            }
        """)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.setSpacing(5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search transactions...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #2A2D35;
                border-radius: 5px;
                background-color: #2A2D35;
                color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        
        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(30, 30)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0B90B;
                color: black;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F8C032;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        # Organize filters in layout
        filter_layout.addLayout(period_layout)
        filter_layout.addLayout(type_layout)
        filter_layout.addStretch()
        filter_layout.addLayout(search_layout)
        
        # Enhanced transaction table with modern styling
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)  # Added a status column
        self.transaction_table.setHorizontalHeaderLabels(["Action", "Symbol", "Shares", "Price", "Date", "Status"])
        self.transaction_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: #2A2D35;
                color: white;
                font-size: 13px;
                selection-background-color: rgba(240, 185, 11, 0.2);
                selection-color: white;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2A2D35;
            }
            QTableWidget::item:selected {
                background-color: rgba(240, 185, 11, 0.2);
            }
            QTableWidget::item:hover {
                background-color: rgba(42, 45, 53, 0.5);
            }
            QHeaderView::section {
                background-color: #2A2D35;
                color: #F0B90B;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget QScrollBar:vertical {
                border: none;
                background-color: #1E2026;
                width: 12px;
                margin: 0px;
            }
            QTableWidget QScrollBar::handle:vertical {
                background-color: #2A2D35;
                min-height: 30px;
                border-radius: 6px;
            }
            QTableWidget QScrollBar::handle:vertical:hover {
                background-color: #F0B90B;
            }
            QTableWidget QScrollBar::add-line:vertical, 
            QTableWidget QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.transaction_table.horizontalHeader().setStretchLastSection(True)
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_table.verticalHeader().setVisible(False)
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transaction_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.transaction_table.setAlternatingRowColors(True)
        self.transaction_table.setShowGrid(False)
        self.transaction_table.setMinimumHeight(400)  # Ensure enough height for data
        
        # Add pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setAlignment(Qt.AlignCenter)
        
        prev_btn = QPushButton("◀ Previous")
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3A3D45;
            }
            QPushButton:disabled {
                background-color: #1E2026;
                color: #666666;
            }
        """)
        
        # Page number indicator
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet("font-size: 13px; color: #BBBBBB; margin: 0 15px;")
        
        next_btn = QPushButton("Next ▶")
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3A3D45;
            }
            QPushButton:disabled {
                background-color: #1E2026;
                color: #666666;
            }
        """)
        
        pagination_layout.addWidget(prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(next_btn)
        
        # Export and action buttons
        action_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export Transactions")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A3D45;
            }
        """)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A3D45;
            }
        """)
        
        # Remove icon references that might be causing issues
        # export_btn.setIcon(QIcon(":/icons/export.png"))
        # refresh_btn.setIcon(QIcon(":/icons/refresh.png"))
        
        action_layout.addWidget(export_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        
        # Add all components to table section
        table_layout.addLayout(filter_layout)
        table_layout.addWidget(self.transaction_table)
        table_layout.addLayout(pagination_layout)
        table_layout.addLayout(action_layout)
        
        # Add sections to main layout
        layout.addWidget(header_section)
        layout.addWidget(table_section)
        
        # Set widget for scroll area
        scroll_area.setWidget(widget)
        
        return scroll_area

    def create_performance_section(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0C0D10;
            }
        """)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(20)
        
        # Header section
        header_section = QFrame()
        header_section.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_section)
        
        title = QLabel("Portfolio Performance")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        
        subtitle = QLabel("Analyze your investment growth over time")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #999999;
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        # Performance chart
        chart_section = QFrame()
        chart_section.setMinimumHeight(400)
        chart_section.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        chart_layout = QVBoxLayout(chart_section)
        
        chart = QChart()
        chart.setTitle("Portfolio Value")
        chart.setTitleFont(QFont("Segoe UI", 16))
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundBrush(QColor("#1E2026"))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QLineSeries()
        series.setName("Portfolio Value")
        series.setPen(QPen(QColor("#F0B90B"), 2))
        
        # Sample data
        for i in range(10):
            series.append(i, 10000 + i * 500 + (i * i * 10))
        
        chart.addSeries(series)
        
        # Set up axes
        axis_x = QValueAxis()
        axis_x.setLabelsColor(QColor("#FFFFFF"))
        axis_x.setGridLineColor(QColor("#2A2D35"))
        axis_x.setLinePen(QPen(QColor("#2A2D35"), 1))
        
        axis_y = QValueAxis()
        axis_y.setLabelsColor(QColor("#FFFFFF"))
        axis_y.setGridLineColor(QColor("#2A2D35"))
        axis_y.setLinePen(QPen(QColor("#2A2D35"), 1))
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("""
            background-color: #1E2026;
            border: none;
        """)
        
        chart_layout.addWidget(chart_view)
        
        # Stats section
        stats_section = QFrame()
        stats_section.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QHBoxLayout(stats_section)
        
        # ROI stats
        roi_frame = QFrame()
        roi_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2D35;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        roi_layout = QVBoxLayout(roi_frame)
        
        roi_title = QLabel("Return on Investment")
        roi_title.setStyleSheet("font-size: 16px; color: #999999; font-weight: bold;")
        
        roi_value = QLabel("+21.5%")
        roi_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #00C087;")
        
        roi_layout.addWidget(roi_title)
        roi_layout.addWidget(roi_value)
        
        # Best performer
        best_frame = QFrame()
        best_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2D35;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        best_layout = QVBoxLayout(best_frame)
        
        best_title = QLabel("Best Performer")
        best_title.setStyleSheet("font-size: 16px; color: #999999; font-weight: bold;")
        
        best_stock = QLabel("AAPL")
        best_stock.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        best_value = QLabel("+45.2%")
        best_value.setStyleSheet("font-size: 20px; color: #00C087;")
        
        best_layout.addWidget(best_title)
        best_layout.addWidget(best_stock)
        best_layout.addWidget(best_value)
        
        # Worst performer
        worst_frame = QFrame()
        worst_frame.setStyleSheet("""
            QFrame {
                background-color: #2A2D35;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        worst_layout = QVBoxLayout(worst_frame)
        
        worst_title = QLabel("Worst Performer")
        worst_title.setStyleSheet("font-size: 16px; color: #999999; font-weight: bold;")
        
        worst_stock = QLabel("META")
        worst_stock.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        worst_value = QLabel("-12.8%")
        worst_value.setStyleSheet("font-size: 20px; color: #F6465D;")
        
        worst_layout.addWidget(worst_title)
        worst_layout.addWidget(worst_stock)
        worst_layout.addWidget(worst_value)
        
        stats_layout.addWidget(roi_frame)
        stats_layout.addWidget(best_frame)
        stats_layout.addWidget(worst_frame)
        
        # Add all sections to main layout
        layout.addWidget(header_section)
        layout.addWidget(chart_section)
        layout.addWidget(stats_section)
        
        scroll_area.setWidget(widget)
        return scroll_area

    def _handle_search_click(self):
        symbol = self.search_input.text().strip().upper()
        period = self.period_selector.currentText()
        if symbol:
            self.stock_search_requested.emit(symbol, period)

    def update_stock_search_result(self, name: str, price: float, history: List[tuple]):
        """Display stock history chart and metrics in the search view."""
        if not history:
            self.search_info_label.setText(f"No data found for {name}.")
            self.chart_view.setChart(QChart())  # Clear chart
            return

        # Sort history by timestamp
        history.sort(key=lambda x: x[0])
        timestamps, values = zip(*history)

        # Build series
        series = QLineSeries()
        for dt, val in zip(timestamps, values):
            ts = QDateTime.fromSecsSinceEpoch(int(dt.timestamp()))
            series.append(ts.toMSecsSinceEpoch(), val)

        # Create chart
        chart = QChart()
        chart.setTitle(f"{name} Price Trend")
        chart.setTitleFont(QFont("Segoe UI", 15, QFont.Bold))
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundVisible(False)
        chart.setBackgroundBrush(QBrush(QColor("#1E2026")))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.addSeries(series)

        # X Axis
        x_axis = QDateTimeAxis()
        x_axis.setFormat("MMM dd, yyyy")
        x_axis.setLabelsColor(QColor("#FFFFFF"))
        x_axis.setGridLineColor(QColor("#444444"))
        x_axis.setTitleText("Date")
        x_axis.setRange(
            QDateTime.fromSecsSinceEpoch(int(timestamps[0].timestamp())),
            QDateTime.fromSecsSinceEpoch(int(timestamps[-1].timestamp()))
        )
        chart.addAxis(x_axis, Qt.AlignBottom)
        series.attachAxis(x_axis)

        # Y Axis
        min_val, max_val = min(values), max(values)
        y_axis = QValueAxis()
        y_axis.setLabelFormat("$%.2f")
        y_axis.setLabelsColor(QColor("#FFFFFF"))
        y_axis.setGridLineColor(QColor("#444444"))
        y_axis.setTitleText("Price")
        y_axis.setRange(min_val * 0.95, max_val * 1.05)
        chart.addAxis(y_axis, Qt.AlignLeft)
        series.attachAxis(y_axis)

        # Apply to chart view
        self.chart_view.setChart(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setAutoFillBackground(False)
        self.chart_view.setStyleSheet("background: transparent; border: none;")
        self.chart_view.setBackgroundBrush(QBrush(Qt.transparent))

        # Update info label
        self.search_info_label.setText(f"{name} - Current: ${price:.2f}")

        # Calculate and format metrics
        first_price = values[0]
        last_price = values[-1]
        price_change = ((last_price - first_price) / first_price) * 100 if first_price else 0
        market_cap = last_price * 1_000_000_000  # Placeholder
        mc_display = (
            f"${market_cap / 1e12:.2f}T" if market_cap >= 1e12 else
            f"${market_cap / 1e9:.2f}B" if market_cap >= 1e9 else
            f"${market_cap / 1e6:.2f}M"
        )

        metrics = {
            "Current Price": f"${last_price:.2f}",
            "52-Week High": f"${max_val:.2f}",
            "52-Week Low": f"${min_val:.2f}",
            "% Change": f"{price_change:+.2f}%",
            "Market Cap": mc_display,
            "Volume": "1.2M"
        }

        for frame in self.stats_frames:
            title_label = frame.findChild(QLabel, "metric_title")
            value_label = frame.findChild(QLabel, "metric_value")
            if not title_label or not value_label:
                continue

            key = title_label.text()
            value = metrics.get(key, "--")
            value_label.setText(value)

            # Color coding
            color = (
                "#00C087" if key == "% Change" and price_change >= 0 else
                "#F6465D" if key == "% Change" and price_change < 0 else
                "#00C087" if key == "52-Week High" else
                "#F6465D" if key == "52-Week Low" else
                "white"
            )
            value_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def create_stock_search_section(self):
        # Main widget with no scrolling
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #0C0D10;")
        
        # Use a grid layout for better space utilization
        main_layout = QGridLayout(main_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(5)
        
        # Compact header with search controls
        header_section = QFrame()
        header_section.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 4px;
            }
        """)
        header_section.setMaximumHeight(70)
        
        header_layout = QHBoxLayout(header_section)
        header_layout.setContentsMargins(8, 5, 8, 5)
        
        # Title section
        title_section = QVBoxLayout()
        title = QLabel("STOCK SEARCH")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F0B90B;")
        
        subtitle = QLabel("Research stocks and view performance")
        subtitle.setStyleSheet("font-size: 10px; color: #999999;")
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        # Search inputs section
        search_section = QHBoxLayout()
        search_section.setSpacing(8)
        
        # Symbol input
        symbol_layout = QVBoxLayout()
        symbol_layout.setSpacing(1)
        
        symbol_label = QLabel("Symbol")
        symbol_label.setStyleSheet("font-size: 10px; color: #999999;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter stock symbol (e.g. AAPL)")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #2A2D35;
                border-radius: 3px;
                background-color: #2A2D35;
                color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        
        symbol_layout.addWidget(symbol_label)
        symbol_layout.addWidget(self.search_input)
        
        # Period selector
        period_layout = QVBoxLayout()
        period_layout.setSpacing(1)
        
        period_label = QLabel("Time Period")
        period_label.setStyleSheet("font-size: 10px; color: #999999;")
        
        self.period_selector = QComboBox()
        self.period_selector.addItems(["1W", "1M", "3M", "6M", "1Y", "5Y", "10Y"])
        self.period_selector.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #2A2D35;
                border-radius: 3px;
                background-color: #2A2D35;
                color: white;
                font-size: 11px;
                min-width: 80px;
            }
            QComboBox:focus {
                border-color: #F0B90B;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2D35;
                color: white;
                border: 1px solid #F0B90B;
                selection-background-color: #F0B90B;
                selection-color: black;
            }
        """)
        
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_selector)
        
        # Search button
        button_layout = QVBoxLayout()
        button_layout.setSpacing(1)
        button_layout.addWidget(QLabel(""))  # Spacer for alignment
        
        search_btn = QPushButton("SEARCH")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0B90B;
                color: black;
                padding: 6px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #F8C032;
            }
        """)
        search_btn.clicked.connect(self._handle_search_click)
        
        button_layout.addWidget(search_btn)
        
        search_section.addLayout(symbol_layout, 3)
        search_section.addLayout(period_layout, 1)
        search_section.addLayout(button_layout, 1)
        
        header_layout.addLayout(title_section, 1)
        header_layout.addLayout(search_section, 2)
        
        # Stock info and chart section
        info_section = QFrame()
        info_section.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 4px;
            }
        """)
        
        info_layout = QVBoxLayout(info_section)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(8)
        
        # Stock info header
        info_header = QHBoxLayout()
        
        self.search_info_label = QLabel("Enter a stock symbol above to see information")
        self.search_info_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)
        
        info_type = QLabel("PRICE HISTORY")
        info_type.setStyleSheet("font-size: 10px; color: #999999;")
        info_type.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        info_header.addWidget(self.search_info_label)
        info_header.addStretch()
        info_header.addWidget(info_type)
        
        # Price chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(250)
        self.chart_view.setStyleSheet("""
            background-color: #1E2026;
            border: none;
            color: white;
        """)
        
        info_layout.addLayout(info_header)
        info_layout.addWidget(self.chart_view)
        
        # Improved metrics section with two rows for better organization
        stats_section = QFrame()
        stats_section.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 4px;
            }
        """)
        stats_section.setMaximumHeight(130)  # Increased height for two rows
        
        stats_layout = QVBoxLayout(stats_section)
        stats_layout.setContentsMargins(10, 8, 10, 8)
        stats_layout.setSpacing(8)
        
        # Title for stats
        stats_header = QHBoxLayout()
        stats_title = QLabel("KEY METRICS")
        stats_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #F0B90B;")
        
        # Add a refresh button
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(24, 24)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                color: #999999;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34373F;
                color: #F0B90B;
            }
        """)
        
        stats_header.addWidget(stats_title)
        stats_header.addStretch()
        stats_header.addWidget(refresh_btn)
        
        stats_layout.addLayout(stats_header)
        
        # Create two rows of metrics for better organization
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(8)
        
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(8)
        
        # Store frames for later updates
        self.stats_frames = []
        
        # First row metrics
        row1_metrics = [
            {"title": "Current Price", "value": "$0.00", "color": "white"},
            {"title": "52-Week High", "value": "$0.00", "color": "#00C087"},
            {"title": "52-Week Low", "value": "$0.00", "color": "#F6465D"},
        ]
        
        # Second row metrics
        row2_metrics = [
            {"title": "Market Cap", "value": "$0.00", "color": "white"},
            {"title": "Volume", "value": "0", "color": "white"},
            {"title": "% Change", "value": "0.00%", "color": "#999999"},
        ]
        
        # Create first row metrics
        for metric in row1_metrics:
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #2A2D35;
                    border-radius: 4px;
                }}
            """)
            
            metric_layout = QVBoxLayout(metric_frame)
            metric_layout.setContentsMargins(10, 6, 10, 6)
            metric_layout.setSpacing(2)
            
            title = QLabel(metric["title"])
            title.setObjectName("metric_title")
            title.setStyleSheet("font-size: 10px; color: #999999; font-weight: bold;")
            
            value = QLabel(metric["value"])
            value.setObjectName("metric_value")
            value.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {metric['color']};")
            
            metric_layout.addWidget(title)
            metric_layout.addWidget(value)
            
            row1_layout.addWidget(metric_frame)
            self.stats_frames.append(metric_frame)
        
        # Create second row metrics
        for metric in row2_metrics:
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #2A2D35;
                    border-radius: 4px;
                }}
            """)
            
            metric_layout = QVBoxLayout(metric_frame)
            metric_layout.setContentsMargins(10, 6, 10, 6)
            metric_layout.setSpacing(2)
            
            title = QLabel(metric["title"])
            title.setObjectName("metric_title")
            title.setStyleSheet("font-size: 10px; color: #999999; font-weight: bold;")
            
            value = QLabel(metric["value"])
            value.setObjectName("metric_value")
            value.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {metric['color']};")
            
            metric_layout.addWidget(title)
            metric_layout.addWidget(value)
            
            row2_layout.addWidget(metric_frame)
            self.stats_frames.append(metric_frame)
        
        stats_layout.addLayout(row1_layout)
        stats_layout.addLayout(row2_layout)
        
        # Add sections to the main layout
        main_layout.addWidget(header_section, 0, 0, 1, 1)  # Header
        main_layout.addWidget(info_section, 1, 0, 3, 1)    # Chart area
        main_layout.addWidget(stats_section, 4, 0, 1, 1)   # Statistics
        
        # Set row stretches to prioritize the chart area
        main_layout.setRowStretch(0, 1)  # Header (small)
        main_layout.setRowStretch(1, 7)  # Chart (large)
        main_layout.setRowStretch(4, 2)  # Stats (larger now for two rows)
        
        return main_widget

    def update_total_gain_loss(self, amount: float):
        color = "#00C087" if amount > 0 else "#F6465D" if amount < 0 else "white"
        sign = "+" if amount > 0 else ""
        self.total_gain_loss_label.setText(f"Total Gain/Loss: <span style='color:{color}'>{sign}${amount:,.2f}</span>")

    def set_username(self, username: str):
        self.username_label.setText(username)

    def update_profile_image(self, image_url: str):
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.profile_pic_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print("Image load error:", e)

    def update_portfolio_summary(self, total_value: float, daily_change: float):
        self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")

    def update_holdings_table(self, holdings):
        self.stock_table.setRowCount(len(holdings))
        for row, stock in enumerate(holdings):
            # Symbol
            symbol_item = QTableWidgetItem(stock.symbol)
            symbol_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            # Shares
            shares_item = QTableWidgetItem(str(stock.shares))
            
            # Purchase price
            purchase_item = QTableWidgetItem(f"${stock.purchase_price:,.2f}")
            
            # Current price
            current_item = QTableWidgetItem(f"${stock.current_price:,.2f}")
            
            # Value
            value_item = QTableWidgetItem(f"${stock.value:,.2f}")
            value_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            # Gain/Loss
            gain_loss_item = QTableWidgetItem(f"${stock.gain_loss:,.2f}")
            gain_loss_item.setForeground(
                QColor("#00C087") if stock.gain_loss > 0 
                else QColor("#F6465D") if stock.gain_loss < 0 
                else QColor("white")
            )
            
            self.stock_table.setItem(row, 0, symbol_item)
            self.stock_table.setItem(row, 1, shares_item)
            self.stock_table.setItem(row, 2, purchase_item)
            self.stock_table.setItem(row, 3, current_item)
            self.stock_table.setItem(row, 4, value_item)
            self.stock_table.setItem(row, 5, gain_loss_item)

    def show_image_selector(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Profile Image")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E2026;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        dialog.setFixedWidth(500)  # More compact dialog
        
        layout = QGridLayout(dialog)
        layout.setSpacing(10)
        
        # Profile titles
        profile_titles = [
            "The Default", "Risk Taker", "Business Savvy", "The Analyst",
            "Growth Guru", "Steady Saver", "Market Hawk", "The Bull", "The Bear"
        ]
        
        for i in range(9):
            image_name = "profile_default" if i == 0 else f"profile_{i}"
            image_url = f"https://res.cloudinary.com/dxohlu5cy/image/upload/default/{image_name}.png"
            
            # Container widget
            container = QFrame()
            container.setStyleSheet("""
                QFrame {
                    background-color: #2A2D35;
                    border-radius: 6px;
                    padding: 5px;
                }
                QFrame:hover {
                    background-color: #34373F;
                    border: 1px solid #F0B90B;
                }
            """)
            
            container_layout = QVBoxLayout(container)
            container_layout.setAlignment(Qt.AlignCenter)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(3)
            
            # Image button
            button = QPushButton()
            button.setFixedSize(60, 60)  # Smaller images
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border-radius: 30px;
                    border: 2px solid #F0B90B;
                }
                QPushButton:hover {
                    border: 3px solid #F0B90B;
                }
            """)
            
            pixmap = QPixmap()
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    pixmap.loadFromData(response.content)
                    button.setIcon(QIcon(pixmap))
                    button.setIconSize(button.size())
            except Exception as e:
                print(f"Error loading image {i}: {e}")
                continue
            
            button.clicked.connect(lambda _, index=i: self.select_preset(dialog, index))
            
            # Label
            label = QLabel(profile_titles[i])
            label.setStyleSheet("""
                font-size: 11px; 
                color: white;
                margin-top: 2px;
            """)
            label.setAlignment(Qt.AlignCenter)
            
            container_layout.addWidget(button, 0, Qt.AlignCenter)
            container_layout.addWidget(label, 0, Qt.AlignCenter)
            
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
            if shares <= 0:
                raise ValueError("Shares must be positive")
                
            self.buy_requested.emit(symbol, shares)
            # Clear inputs after successful purchase
            self.symbol_input.clear()
            self.shares_input.clear()
            
        except ValueError as e:
            # You could show an error message dialog here
            print(f"Invalid input: {e}")

    def _handle_sell(self):
        symbol = self.symbol_input.text().upper()
        try:
            shares = int(self.shares_input.text())
            if shares <= 0:
                raise ValueError("Shares must be positive")
                
            self.sell_requested.emit(symbol, shares)
            # Clear inputs after successful sale
            self.symbol_input.clear()
            self.shares_input.clear()
            
        except ValueError as e:
            # You could show an error message dialog here
            print(f"Invalid input: {e}")
        symbol = self.symbol_input.text().upper()



from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QGridLayout,
    QHeaderView, QStackedWidget, QTabWidget, QToolBar,
    QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QColor, QIcon, QFont

class LoginView(QWidget):
    login_requested = Signal(str, str)
    signup_requested = Signal(str, str)    
    forgot_password_requested = Signal(str)
    login_successful = Signal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Connect keyboard shortcuts
        self.password_input.returnPressed.connect(self._handle_login_click)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())

    def setup_ui(self):
        # Main layout with proper spacing
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Set dark theme background
        self.setStyleSheet("background-color: #0A0C10;")
        
        # Create a split layout with proper proportions
        left_panel = QWidget()
        right_panel = QWidget()
        
        # Left panel styling (marketing/branding side)
        left_panel.setStyleSheet("""
            background-color: #12141A;
        """)
        
        # Right panel styling (login form side)
        right_panel.setStyleSheet("""
            background-color: #12141A;
        """)
        
        # Set up content for left panel (branding area)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 50, 50, 50)
        left_layout.setSpacing(30)
        
        # Logo and name in header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Clean logo (would be better as SVG in production)
        logo_icon = QLabel()
        logo_pixmap = QPixmap(":/icons/chart.png")
        if logo_pixmap.isNull():
            # Fallback if image not available
            logo_icon.setText("📈")
            logo_icon.setStyleSheet("font-size: 28px;")
        else:
            logo_icon.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Brand name with simpler styling
        brand_name = QLabel("STOCK<span style='color: #F0B90B;'>FOLIO</span>")
        brand_name.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: white;
            letter-spacing: 0.5px;
        """)
        brand_name.setTextFormat(Qt.RichText)
        
        header_layout.addWidget(logo_icon)
        header_layout.addWidget(brand_name)
        header_layout.addStretch()
        
        left_layout.addLayout(header_layout)
        
        # Main marketing message
        message_container = QWidget()
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(12)
        
        # Headline with accent color
        headline = QLabel("Your Portfolio,<br>Your <span style='color: #F0B90B;'>Future</span>")
        headline.setTextFormat(Qt.RichText)
        headline.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: white;
            line-height: 1.2;
        """)
        
        # Subtitle with good contrast
        subtitle = QLabel("Track, analyze, and grow your investments in one place")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #B0B0B0;
            margin-top: 5px;
        """)
        
        message_layout.addWidget(headline)
        message_layout.addWidget(subtitle)
        
        left_layout.addWidget(message_container)
        
        # Trading volume card - cleaner approach
        trading_card = QWidget()
        trading_card.setStyleSheet("""
            background-color: #1A1D24;
            border-radius: 8px;
        """)
        trading_layout = QVBoxLayout(trading_card)
        trading_layout.setContentsMargins(24, 20, 24, 20)
        trading_layout.setSpacing(8)
        
        trading_label = QLabel("24H TRADING VOLUME")
        trading_label.setStyleSheet("""
            font-size: 13px;
            color: #8A8D93;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)
        
        trading_value = QLabel("$14,755,026,601")
        trading_value.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #F0B90B;
        """)
        
        trading_layout.addWidget(trading_label)
        trading_layout.addWidget(trading_value)
        
        left_layout.addWidget(trading_card)
        
        # Stats grid - cleaner implementation
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        
        # Function to create clean stat cards
        def create_stat_card(icon, value, label):
            card = QWidget()
            card.setStyleSheet("""
                background-color: #1A1D24;
                border-radius: 8px;
            """)
            
            layout = QHBoxLayout(card)
            layout.setContentsMargins(20, 16, 20, 16)
            
            # Icon with appropriate spacing
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("""
                font-size: 20px;
                margin-right: 12px;
            """)
            
            # Text container
            text_container = QVBoxLayout()
            text_container.setSpacing(2)
            
            # Value with emphasis
            value_label = QLabel(value)
            value_label.setStyleSheet("""
                font-size: 18px;
                font-weight: 700;
                color: #F0B90B;
            """)
            
            # Label with lower emphasis
            desc_label = QLabel(label)
            desc_label.setStyleSheet("""
                font-size: 13px;
                color: #8A8D93;
            """)
            
            text_container.addWidget(value_label)
            text_container.addWidget(desc_label)
            
            layout.addWidget(icon_label)
            layout.addLayout(text_container)
            layout.addStretch()
            
            return card
        
        # Create stat cards with clean design
        users_card = create_stat_card("👥", "69M+", "Registered Users")
        countries_card = create_stat_card("🌎", "160+", "Supported Countries")
        stocks_card = create_stat_card("📊", "1,862", "Stocks Listed")
        security_card = create_stat_card("🔒", "100%", "Secure Trading")
        
        # Add cards to grid
        stats_grid.addWidget(users_card, 0, 0)
        stats_grid.addWidget(countries_card, 0, 1)
        stats_grid.addWidget(stocks_card, 1, 0)
        stats_grid.addWidget(security_card, 1, 1)
        
        left_layout.addLayout(stats_grid)
        
        # Footer with support info
        support_label = QLabel("24/7 Support | 100k TPS Matching Engine")
        support_label.setStyleSheet("""
            font-size: 14px;
            color: #8A8D93;
            margin-top: 10px;
        """)
        
        left_layout.addStretch()
        left_layout.addWidget(support_label, alignment=Qt.AlignCenter)
        
        # Set up content for right panel (login form)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 40, 50, 40)  # Proper margins all around
        right_layout.setSpacing(0)
        
        # Center the form with proper spacing
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Login form with clean styling
        login_form = QWidget()
        login_form.setFixedWidth(360)
        
        login_layout = QVBoxLayout(login_form)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(24)
        
        # Form title
        title = QLabel("Stock Portfolio Manager")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: white;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        login_subtitle = QLabel("Sign in to manage your investments")
        login_subtitle.setStyleSheet("""
            font-size: 15px;
            color: #8A8D93;
        """)
        login_subtitle.setAlignment(Qt.AlignCenter)
        
        # Form fields container
        fields_container = QWidget()
        fields_layout = QVBoxLayout(fields_container)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(16)
        
        # Username field with clean design
        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            font-size: 14px;
            color: #C0C0C0;
            font-weight: 500;
            margin-bottom: 6px;
        """)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                background-color: #1A1D24;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #1D2128;
                border: 1px solid #F0B90B;
                padding: 11px 15px;
            }
        """)
        
        # Password field with clean design
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            font-size: 14px;
            color: #C0C0C0;
            font-weight: 500;
            margin-bottom: 6px;
        """)
        
        password_input_container = QHBoxLayout()
        password_input_container.setContentsMargins(0, 0, 0, 0)
        password_input_container.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 40px 12px 16px; /* Extra right padding for the button */
                background-color: #1A1D24;
                border: 1px solid #2A2D35;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)


                
        # Password visibility toggle
        self.show_password_btn = QPushButton("👁")  # Clear text icon instead of using QIcon
        self.show_password_btn.setFixedSize(36, 36)
        self.show_password_btn.setCursor(Qt.PointingHandCursor)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                border: none;
                color: #8A8D93;
                font-size: 18px;
                border-radius: 18px;
                margin-left: 0px;
            }
            QPushButton:hover {
                color: #F0B90B;
                background-color: #34373F;
            }
        """)


        self.show_password_btn.pressed.connect(lambda: self.password_input.setEchoMode(QLineEdit.Normal))
        self.show_password_btn.released.connect(lambda: self.password_input.setEchoMode(QLineEdit.Password))

        
        password_input_container.addWidget(self.password_input)
        password_input_container.addWidget(self.show_password_btn)


        # Forgot password link
        self.forgot_password_label = QLabel("<a href='#' style='color: #F0B90B; text-decoration: none;'>Forgot Password?</a>")
        self.forgot_password_label.setStyleSheet("""
            font-size: 14px;
            padding: 4px 0;
        """)
        self.forgot_password_label.setAlignment(Qt.AlignRight)
        self.forgot_password_label.setCursor(Qt.PointingHandCursor)
        self.forgot_password_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.forgot_password_label.setOpenExternalLinks(False)
        self.forgot_password_label.linkActivated.connect(self._handle_forgot_password)
        
        # Error message area
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            font-size: 14px;
            color: #FF6B6B;
            background-color: rgba(255, 107, 107, 0.1);
            padding: 12px;
            border-radius: 6px;
            margin-top: 6px;
        """)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        
        # Add username and password fields to form
        username_container = QVBoxLayout()
        username_container.setSpacing(4)
        username_container.addWidget(username_label)
        username_container.addWidget(self.username_input)
        
        password_container = QVBoxLayout()
        password_container.setSpacing(4)
        password_container.addWidget(password_label)
        password_container.addLayout(password_input_container)
        password_container.addWidget(self.forgot_password_label)
        
        fields_layout.addLayout(username_container)
        fields_layout.addLayout(password_container)
        fields_layout.addWidget(self.error_label)
        
        # Login button with clean design
        login_button = QPushButton("LOGIN")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #F0B90B;
                color: #000000;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }
            QPushButton:hover {
                background-color: #F8C032;
            }
            QPushButton:pressed {
                background-color: #E0AA0B;
            }
        """)
        login_button.clicked.connect(self._handle_login_click)
        
        # Sign up area
        signup_container = QVBoxLayout()
        signup_container.setSpacing(16)
        signup_container.setContentsMargins(0, 16, 0, 0)
        
        signup_text = QLabel("Don't have an account?")
        signup_text.setStyleSheet("""
            font-size: 14px;
            color: #8A8D93;
        """)
        signup_text.setAlignment(Qt.AlignCenter)
        
        signup_button = QPushButton("SIGN UP")
        signup_button.setCursor(Qt.PointingHandCursor)
        signup_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #F0B90B;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                border: 1px solid #F0B90B;
            }
            QPushButton:hover {
                background-color: rgba(240, 185, 11, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(240, 185, 11, 0.15);
            }
        """)
        signup_button.clicked.connect(self._handle_signup_click)
        
        signup_container.addWidget(signup_text)
        signup_container.addWidget(signup_button)
        
        # Assemble form components
        login_layout.addWidget(title)
        login_layout.addWidget(login_subtitle)
        login_layout.addWidget(fields_container)
        login_layout.addSpacing(8)
        login_layout.addWidget(login_button)
        login_layout.addLayout(signup_container)
        
        # Center the form in the right panel
        right_layout.addStretch(1)
        right_layout.addWidget(login_form, 0, Qt.AlignCenter)
        right_layout.addStretch(1)
        
        # Add panels to main layout with appropriate proportions
        main_layout.addWidget(left_panel, 1)  # 50% width
        main_layout.addWidget(right_panel, 1)  # 50% width
        
        # Set system font stack
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
            }
        """)

        
        # Set proper tab order
        QWidget.setTabOrder(self.username_input, self.password_input)
        QWidget.setTabOrder(self.password_input, login_button)
        QWidget.setTabOrder(login_button, signup_button)
    
    def show_error(self, message):
        """Shows error message with cleaner styling"""
        self.error_label.setText(message)
        self.error_label.show()
    
    def clear_error(self):
        """Clears error message"""
        self.error_label.hide()
    
    def clear_inputs(self):
        """Clears the username and password fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.clear_error()
    
    def _handle_login_click(self):
        """Handles login button click with improved validation"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username and not password:
            self.show_error("Please enter your username and password")
        elif not username:
            self.show_error("Please enter your username")
            self.username_input.setFocus()
        elif not password:
            self.show_error("Please enter your password")
            self.password_input.setFocus()
        else:
            self.clear_error()
            self.login_requested.emit(username, password)
    
    def _handle_signup_click(self):
        """Handles signup button click with validation"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username and not password:
            self.show_error("Please enter a username and password to create your account")
        elif not username:
            self.show_error("Please enter a username")
            self.username_input.setFocus()
        elif not password:
            self.show_error("Please enter a password")
            self.password_input.setFocus()
        elif len(password) < 8:
            self.show_error("Your password must be at least 8 characters long")
            self.password_input.setFocus()
        else:
            self.clear_error()
            self.signup_requested.emit(username, password)
    
    def _handle_forgot_password(self):
        """Handles forgot password link click"""
        username = self.username_input.text().strip()
        if not username:
            self.show_error("Please enter your username to reset your password")
            self.username_input.setFocus()
        else:
            self.clear_error()
            self.forgot_password_requested.emit(username)
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

        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()



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

    def show_loading_message(self, message="Processing..."):
        self.loading_overlay.set_message(message)
        self.loading_overlay.switch_to_indeterminate()
        self.loading_overlay.show()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

    def hide_loading_message(self):
        self.loading_overlay.hide()
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()


    def handle_login(self, username, password):
        """Handle login with loading indicator"""
        self.show_loading_message(f"Logging in as {username}...")
        
        # Use a timer to simulate network delay and allow UI to update
        QTimer.singleShot(2000, lambda: self._process_login(username, password))

    def _process_login(self, username, password):
        """Process the actual login after showing loading indicator"""
        # This would normally call your authentication service
        # For demo, we'll simulate successful login
        if username == "demo" and password == "password":
            self.hide_loading_message()
            self.login_view.clear_inputs()
            self.show_portfolio("user123")
        else:
            self.hide_loading_message()
            self.login_view.show_error("Invalid username or password")

    def handle_signup(self, username, password):
        """Handle signup with loading indicator"""
        self.show_loading_message(f"Creating account for {username}...")
        
        # Use a timer to simulate network delay and allow UI to update
        QTimer.singleShot(2000, lambda: self._process_login(username, password))

    def _process_signup(self, username, password):
        """Process the actual signup after showing loading indicator"""
        # This would normally call your authentication service
        self.hide_loading_message()
        self.login_view.clear_inputs()
        self.show_portfolio("user123")  # Always succeed for demo

    def handle_trade(self, action, symbol, shares):
        self.show_loading_message(f"{action.capitalize()}ing {shares} shares of {symbol}...")
        QTimer.singleShot(2000, lambda: self._process_trade(action, symbol, shares))


    def _process_trade(self, action, symbol, shares):
        """Process the actual trade after showing loading indicator"""
        # This would normally call your portfolio service
        import random
        success = random.random() < 0.9  # 90% success rate for demo
        
        self.hide_loading_message()
        verb_past = {
            "buy": "bought",
            "sell": "sold"
        }.get(action.lower(), f"{action}ed")

        if success:
            QMessageBox.information(
                self,
                "Trade Completed 🎉",
                f"You've successfully {verb_past} {shares} share{'s' if shares != 1 else ''} of {symbol}!\nYour portfolio has been updated.",
                QMessageBox.Ok
            )
            # Refresh portfolio data
        else:
            QMessageBox.warning(
                self,
                "Trade Failed 😞",
                f"Oops! We couldn't complete your request to {action} {shares} share{'s' if shares != 1 else ''} of {symbol}.\nPlease try again or check your connection.",
                QMessageBox.Ok
            )



    def handle_stock_search(self, symbol, period):
        """Handle stock search with loading indicator"""
        self.show_loading_message(f"Searching for {symbol} data...")
        
        # Use a timer to simulate network delay and allow UI to update
        QTimer.singleShot(800, lambda: self._process_stock_search(symbol, period))

    def _process_stock_search(self, symbol, period):
        """Process the actual stock search after showing loading indicator"""
        # For demo purposes, match common symbols
        common_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        
        self.hide_loading_message()
        try:
            history, name, price = self.api.get_stock_data(symbol, period)
            self.portfolio_view.update_stock_search_result(name, price, history)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Search Failed",
                f"Could not load data for {symbol}: {e}",
                QMessageBox.Ok
            )


    def connect_signals(self):
        self.login_view.login_successful.connect(self.show_portfolio)
        self.login_view.login_requested.connect(self.handle_login)
        self.login_view.signup_requested.connect(self.handle_signup)
        
        self.portfolio_view.buy_requested.connect(lambda symbol, shares: self.handle_trade("buy", symbol, shares))
        self.portfolio_view.sell_requested.connect(lambda symbol, shares: self.handle_trade("sell", symbol, shares))
        self.portfolio_view.stock_search_requested.connect(self.handle_stock_search)
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
        default_url = "https://res.cloudinary.com/dxohlu5cy/image/upload/default/profile_default.png"
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
        self.ai_chat_view = AiChatView()
        self.ai_chat_presenter = AiChatPresenter(
            self.ai_chat_view,
            AiAdvisorService(),
            self.current_user_id
        )
        self.ai_chat_view.show()


class LoadingOverlay(QWidget):
    """Creates an overlay with a loading spinner and optional text."""
    
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        
        # Make the widget cover the parent
        self.setParent(parent)
        self.resize(parent.size())
        self.move(0, 0)
        
        # Semi-transparent background
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 5px;
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container for spinner and message
        container = QWidget()
        container.setMaximumWidth(300)
        container.setMaximumHeight(150)
        container.setStyleSheet("""
            background-color: #1E2026;
            border-radius: 10px;
            border: 1px solid #2C313A;
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignCenter)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)  # Determinate range
        self.progress_bar.setValue(0)
        self.progress_value = 0
        self.progress_direction = 1
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumWidth(200)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2A2D35;
                border-radius: 6px;
                background-color: #2A2D35;
                height: 10px;
            }
            
            QProgressBar::chunk {
                background-color: #F0B90B;
                border-radius: 5px;
            }
        """)
        
        # Message Label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            margin-top: 10px;
        """)
        
        # Add to container
        container_layout.addWidget(self.progress_bar)
        container_layout.addWidget(self.message_label)
        
        # Add container to main layout
        layout.addWidget(container)
        
        # Create a timer to pulse the progress bar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update every 100ms
        self.progress_value = 0
        self.progress_direction = 1
        
        # Make overlay visible on top
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Show the overlay
        QTimer.singleShot(0, self.center_overlay)

    def update_progress(self):
        self.progress_value += self.progress_direction * 3  # Speed multiplier

        if self.progress_value >= 100:
            self.progress_direction = -1
        elif self.progress_value <= 0:
            self.progress_direction = 1

        self.progress_bar.setValue(self.progress_value)


    
    def set_progress(self, value, maximum=100):
        """Set determinate progress."""
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)
    
    def set_message(self, message):
        """Update the message."""
        self.message_label.setText(message)
    
    def switch_to_indeterminate(self):
        """Switch to indeterminate mode."""
        self.progress_bar.setRange(0, 0)
    
    def switch_to_determinate(self, maximum=100):
        """Switch to determinate mode."""
        self.progress_bar.setRange(0, maximum)
        self.progress_value = 0
        self.progress_direction = 1
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.center_overlay)

    def center_overlay(self):
        if self.parent():
            self.resize(self.parent().size())
            self.move(0, 0)
            self.raise_()

