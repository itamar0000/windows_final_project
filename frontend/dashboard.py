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
                margin-right: -8px;
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
            self.chart_view.setChart(QChart())  # clear chart view
            return

        # Sort and separate history
        history.sort(key=lambda x: x[0])
        timestamps, values = zip(*history)
        print(len(history))
        print(len(history))
        print(len(history))
        print(len(history))
        print(len(history))
        # Convert to QLineSeries
        series = QLineSeries()
        for dt, val in zip(timestamps, values):
            ts = QDateTime.fromSecsSinceEpoch(int(dt.timestamp()))
            series.append(ts.toMSecsSinceEpoch(), val)

        # Chart creation
        chart = QChart()
        chart.setTitle(f"{name} Price Trend")
        chart.setTitleFont(QFont("Segoe UI", 15, QFont.Bold))
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundBrush(QColor("#1E2026"))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.addSeries(series)

        # X Axis (Date)
        x_axis = QDateTimeAxis()
        x_axis.setFormat("MMM dd, yyyy")
        x_axis.setLabelsColor(QColor("#FFFFFF"))
        x_axis.setGridLineColor(QColor("#444"))
        x_axis.setTitleText("Date")
        x_axis.setRange(
            QDateTime.fromSecsSinceEpoch(int(timestamps[0].timestamp())),
            QDateTime.fromSecsSinceEpoch(int(timestamps[-1].timestamp()))
        )
        chart.addAxis(x_axis, Qt.AlignBottom)
        series.attachAxis(x_axis)

        # Y Axis (Price)
        min_val, max_val = min(values), max(values)
        y_axis = QValueAxis()
        y_axis.setLabelFormat("$%.2f")
        y_axis.setLabelsColor(QColor("#FFFFFF"))
        y_axis.setGridLineColor(QColor("#444"))
        y_axis.setTitleText("Price")
        y_axis.setRange(min_val * 0.95, max_val * 1.05)
        chart.addAxis(y_axis, Qt.AlignLeft)
        series.attachAxis(y_axis)

        # Apply to chart view
        self.chart_view.setChart(chart)

        # Update info label
        self.search_info_label.setText(f"{name} - Current: ${price:.2f}")

        # Calculate stats
        first_price = values[0]
        last_price = values[-1]
        price_change = ((last_price - first_price) / first_price) * 100 if first_price else 0
        high = max_val
        low = min_val
        volume = "1.2M"
        market_cap = last_price * 1_000_000_000  # placeholder

        # Format market cap nicely
        if market_cap >= 1e12:
            mc_display = f"${market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            mc_display = f"${market_cap / 1e9:.2f}B"
        else:
            mc_display = f"${market_cap / 1e6:.2f}M"

        # Update metric display
        metrics = {
            "Current Price": f"${last_price:.2f}",
            "52-Week High": f"${high:.2f}",
            "52-Week Low": f"${low:.2f}",
            "% Change": f"{price_change:+.2f}%",
            "Market Cap": mc_display,
            "Volume": volume
        }

        for frame in self.stats_frames:
            title_label = frame.findChild(QLabel, "metric_title")
            value_label = frame.findChild(QLabel, "metric_value")
            if not title_label or not value_label:
                continue

            key = title_label.text()
            value = metrics.get(key, "--")
            value_label.setText(value)

            # Color code
            if key == "% Change":
                color = "#00C087" if price_change >= 0 else "#F6465D"
            elif key == "52-Week High":
                color = "#00C087"
            elif key == "52-Week Low":
                color = "#F6465D"
            else:
                color = "white"

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

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create main container with proper background
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: #0C0D10;
            }
        """)
        
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Left panel - Stats
        stats_container = QFrame()
        stats_container.setFixedWidth(500)
        stats_container.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 10px;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(30, 30, 30, 30)
        stats_layout.setSpacing(25)
        
        # Main title for stats
        main_title = QLabel("Never Miss a Beat, With Stock Portfolio")
        main_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-top: 15px;")
        main_title.setWordWrap(True)
        stats_layout.addWidget(main_title)
        
        # Add spacer
        stats_layout.addSpacing(10)
        
        # Trading value
        trading_value = QLabel("$14,755,026,601")
        trading_value.setStyleSheet("font-size: 36px; font-weight: bold; color: #F0B90B;")
        stats_layout.addWidget(trading_value)
        
        trading_label = QLabel("24H Trading Volume (USD)")
        trading_label.setStyleSheet("font-size: 14px; color: #999999; margin-top: -5px;")
        stats_layout.addWidget(trading_label)
        
        # Add spacer
        stats_layout.addSpacing(30)
        
        # Stats grid with spacers
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(20)
        
        # Users stat
        users_layout = QVBoxLayout()
        users_layout.setSpacing(5)
        users_value = QLabel("69M+")
        users_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #F0B90B;")
        users_value.setAlignment(Qt.AlignCenter)
        
        users_label = QLabel("Registered Users")
        users_label.setStyleSheet("font-size: 14px; color: #999999;")
        users_label.setAlignment(Qt.AlignCenter)
        
        users_layout.addWidget(users_value)
        users_layout.addWidget(users_label)
        
        # Countries stat
        countries_layout = QVBoxLayout()
        countries_layout.setSpacing(5)
        countries_value = QLabel("160")
        countries_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #F0B90B;")
        countries_value.setAlignment(Qt.AlignCenter)
        
        countries_label = QLabel("Supported Countries")
        countries_label.setStyleSheet("font-size: 14px; color: #999999;")
        countries_label.setAlignment(Qt.AlignCenter)
        
        countries_layout.addWidget(countries_value)
        countries_layout.addWidget(countries_label)
        
        # Stocks stat
        stocks_layout = QVBoxLayout()
        stocks_layout.setSpacing(5)
        stocks_value = QLabel("1862")
        stocks_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #F0B90B;")
        stocks_value.setAlignment(Qt.AlignCenter)
        
        stocks_label = QLabel("Stocks Listed")
        stocks_label.setStyleSheet("font-size: 14px; color: #999999;")
        stocks_label.setAlignment(Qt.AlignCenter)
        
        stocks_layout.addWidget(stocks_value)
        stocks_layout.addWidget(stocks_label)
        
        stats_grid.addLayout(users_layout)
        stats_grid.addLayout(countries_layout)
        stats_grid.addLayout(stocks_layout)
        
        stats_layout.addLayout(stats_grid)
        
        # Spacer before support info
        stats_layout.addStretch(1)
        
        # Support info
        support_layout = QHBoxLayout()
        support_layout.setContentsMargins(0, 0, 0, 0)
        
        support_icon = QLabel("🎧")  # Headset icon
        support_icon.setStyleSheet("font-size: 20px; color: white;")
        
        support_text = QLabel("24/7 Support | 100k TPS Matching Engine")
        support_text.setStyleSheet("font-size: 14px; color: white;")
        
        support_layout.addWidget(support_icon)
        support_layout.addWidget(support_text)
        support_layout.addStretch()
        
        stats_layout.addLayout(support_layout)
        
        # Right panel - Login form
        login_container = QFrame()
        login_container.setFixedWidth(400)
        login_container.setStyleSheet("""
            QFrame {
                background-color: #1E2026;
                border-radius: 10px;
            }
        """)
        
        form_layout = QVBoxLayout(login_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        # Welcome title
        title = QLabel("Stock Portfolio Manager")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white; 
            margin-bottom: 15px;
        """)
        
        # Subtitle
        subtitle = QLabel("Sign in to manage your investments")
        subtitle.setStyleSheet("font-size: 14px; color: #999999; margin-bottom: 15px;")
        
        # Username Field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 14px; color: #999999; margin-top: 10px;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #2A2D35;
                border-radius: 6px;
                background-color: #2A2D35;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        
        # Password Field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 14px; color: #999999; margin-top: 5px;")
        
        password_container = QHBoxLayout()
        password_container.setContentsMargins(0, 0, 0, 0)
        password_container.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #2A2D35;
                border-radius: 6px;
                background-color: #2A2D35;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedSize(32, 32)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2D35;
                border: 1px solid #2A2D35;
                border-radius: 16px;  /* half of 32 = perfect circle */
                color: #999999;
                font-size: 16px;
                padding-left: 0px;  /* tiny push to the right INSIDE the button */
            }
            QPushButton:hover {
                color: #F0B90B;
            }
        """)


        self.show_password_btn.pressed.connect(lambda: self.password_input.setEchoMode(QLineEdit.Normal))
        self.show_password_btn.released.connect(lambda: self.password_input.setEchoMode(QLineEdit.Password))
        
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.show_password_btn)
        
        # Forgot Password link
        self.forgot_password_label = QLabel("<a href='#'>Forgot Password?</a>")
        self.forgot_password_label.setStyleSheet("font-size: 14px; color: #F0B90B; text-decoration: none;")
        self.forgot_password_label.setAlignment(Qt.AlignRight)
        self.forgot_password_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.forgot_password_label.setOpenExternalLinks(False)
        self.forgot_password_label.linkActivated.connect(self._handle_forgot_password)
        
        # Login Button
        login_button = QPushButton("LOGIN")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #F0B90B;
                color: black;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #F8C032;
            }
            QPushButton:pressed {
                background-color: #E0AA0B;
            }
        """)
        login_button.clicked.connect(self._handle_login_click)
        
        # Sign Up text and button
        signup_text = QLabel("Don't have an account?")
        signup_text.setStyleSheet("font-size: 14px; color: #999999;")
        signup_text.setAlignment(Qt.AlignCenter)
        
        signup_button = QPushButton("SIGN UP")
        signup_button.setCursor(Qt.PointingHandCursor)
        signup_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #F0B90B;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #F0B90B;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(240, 185, 11, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(240, 185, 11, 0.2);
            }
        """)
        signup_button.clicked.connect(self._handle_signup_click)
        
        # Error message label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            font-size: 14px;
            color: #FF4D4F;
            background-color: rgba(255, 77, 79, 0.1);
            padding: 8px;
            border-radius: 4px;
            border-left: 4px solid #FF4D4F;
        """)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        
        # Add form widgets to layout
        form_layout.addWidget(title, alignment=Qt.AlignCenter)
        form_layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addLayout(password_container)
        form_layout.addWidget(self.forgot_password_label)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(login_button)
        form_layout.addSpacing(10)
        form_layout.addWidget(signup_text, alignment=Qt.AlignCenter)
        form_layout.addWidget(signup_button)
        form_layout.addStretch()
        
        # Add both panels to main layout
        main_layout.addWidget(stats_container)
        main_layout.addWidget(login_container)
        
        # Add the main container to the overall layout
        layout.addWidget(main_container)
        self.setLayout(layout)
        
        # Set font family for the entire application
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Set tab order for keyboard navigation
        QWidget.setTabOrder(self.username_input, self.password_input)
        QWidget.setTabOrder(self.password_input, login_button)
        QWidget.setTabOrder(login_button, signup_button)

    def show_error(self, message):
        """Shows error message on failed login attempts"""
        self.error_label.setText(message)
        self.error_label.show()
        
    def clear_error(self):
        """Clears error message"""
        self.error_label.hide()

    def clear_inputs(self):
        """Clears the username and password fields after login."""
        self.username_input.clear()
        self.password_input.clear()
        self.clear_error()

    def _handle_login_click(self):
        """Emits login request signal with username and password."""
        username, password = self.username_input.text(), self.password_input.text()
        
        # Basic validation
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
            
        self.clear_error()
        self.login_requested.emit(username, password)

    def _handle_signup_click(self):
        """Emits signup request signal with username and password."""
        username, password = self.username_input.text(), self.password_input.text()
        
        # Basic validation
        if not username or not password:
            self.show_error("Please enter both username and password to sign up")
            return
            
        self.clear_error()
        self.signup_requested.emit(username, password)

    def _handle_forgot_password(self):
        """Emits forgot password request signal."""
        username = self.username_input.text()
        if not username:
            self.show_error("Please enter your username to reset password")
            return
            
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
        """Shows a simple loading message in the status bar"""
        self.statusBar().showMessage(message)
        # Make the cursor show the busy indicator
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # Force UI update
        QApplication.processEvents()

    def hide_loading_message(self):
        """Hides the loading message"""
        self.statusBar().clearMessage()
        # Restore the normal cursor
        QApplication.restoreOverrideCursor()
        # Force UI update
        QApplication.processEvents()

    def handle_login(self, username, password):
        """Handle login with loading indicator"""
        self.show_loading_message(f"Logging in as {username}...")
        
        # Use a timer to simulate network delay and allow UI to update
        QTimer.singleShot(1000, lambda: self._process_login(username, password))

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
        QTimer.singleShot(1500, lambda: self._process_signup(username, password))

    def _process_signup(self, username, password):
        """Process the actual signup after showing loading indicator"""
        # This would normally call your authentication service
        self.hide_loading_message()
        self.login_view.clear_inputs()
        self.show_portfolio("user123")  # Always succeed for demo

    def handle_trade(self, action, symbol, shares):
        """Handle trade with loading indicator"""
        self.show_loading_message(f"{action.capitalize()}ing {shares} shares of {symbol}...")
        
        # Use a timer to simulate network delay and allow UI to update
        QTimer.singleShot(1000, lambda: self._process_trade(action, symbol, shares))

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



