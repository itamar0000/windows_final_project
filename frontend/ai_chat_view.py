from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

class AiChatView(QWidget):
    send_message_requested = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Window settings
        self.setWindowTitle("AI Investment Advisor")
        self.resize(800, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #0C0D10;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with gradient background
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A1D23, stop:1 #252A34);
                border-bottom: 1px solid #2C313A;
            }
        """)
        header.setMaximumHeight(70)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # AI Advisor title and icon
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        ai_icon = QLabel("🤖")
        ai_icon.setStyleSheet("font-size: 24px;")
        
        title_text = QVBoxLayout()
        title_text.setSpacing(2)
        
        title = QLabel("AI Investment Advisor")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F0B90B;")
        
        subtitle = QLabel("Ask me about stocks, portfolio strategies, and more")
        subtitle.setStyleSheet("font-size: 12px; color: #BBBBBB;")
        
        title_text.addWidget(title)
        title_text.addWidget(subtitle)
        
        title_layout.addWidget(ai_icon)
        title_layout.addLayout(title_text)
        
        # Status indicator
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        
        status_dot = QLabel("•")
        status_dot.setStyleSheet("color: #00C087; font-size: 24px;")
        
        status_label = QLabel("Online")
        status_label.setStyleSheet("color: #00C087; font-size: 14px;")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(status_layout)
        
        # Chat content area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(0)
        
        # Scroll area for chat messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        self.chat_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.chat_content)
        
        # Add welcome message
        self.add_message(
            "Hello! I'm your AI Investment Advisor. I can help you with stock analysis, portfolio optimization, and investment strategies. How can I assist you today?",
            from_user=False
        )
        
        content_layout.addWidget(self.scroll_area)
        
        # Input section with gradient background
        input_section = QFrame()
        input_section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A1D23, stop:1 #252A34);
                border-top: 1px solid #2C313A;
                padding: 15px;
            }
        """)
        
        input_layout = QVBoxLayout(input_section)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(15)
        
        # Quick question buttons
        quick_question_layout = QHBoxLayout()
        quick_question_layout.setSpacing(10)
        
        quick_questions = [
            "Stock Analysis", "Investment Strategies", "Portfolio Tips", "Market Trends"
        ]
        
        for question in quick_questions:
            quick_btn = QPushButton(question)
            quick_btn.setCursor(Qt.PointingHandCursor)
            quick_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2A2D35;
                    color: #BBBBBB;
                    border: none;
                    border-radius: 15px;
                    padding: 5px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #34373F;
                    color: #F0B90B;
                }
            """)
            quick_btn.clicked.connect(lambda _, q=question: self.insert_quick_question(q))
            quick_question_layout.addWidget(quick_btn)
        
        quick_question_layout.addStretch()
        
        # Message input and send button
        message_input_layout = QHBoxLayout()
        message_input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your investment questions here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2A2D35;
                border: 1px solid #2A2D35;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 14px;
                color: white;
            }
            QLineEdit:focus {
                border-color: #F0B90B;
            }
        """)
        self.input_field.returnPressed.connect(self.handle_send_click)
        
        send_button = QPushButton()
        send_button.setFixedSize(44, 44)
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #F0B90B;
                border-radius: 22px;
                border: none;
                color: black;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #F8C032;
            }
            QPushButton:pressed {
                background-color: #E0AA0B;
            }
        """)
        send_button.setText("➤")
        send_button.clicked.connect(self.handle_send_click)
        
        message_input_layout.addWidget(self.input_field)
        message_input_layout.addWidget(send_button)
        
        input_layout.addLayout(quick_question_layout)
        input_layout.addLayout(message_input_layout)
        
        # Add all sections to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(content_container)
        main_layout.addWidget(input_section)
        
        # Set stretch factors
        main_layout.setStretchFactor(header, 0)
        main_layout.setStretchFactor(content_container, 1)
        main_layout.setStretchFactor(input_section, 0)
        
        # Set focus to input field
        self.input_field.setFocus()
    
    def insert_quick_question(self, question):
        """Handle quick question button clicks"""
        quick_question_prompts = {
            "Stock Analysis": "what exactly is a stock?",
            "Investment Strategies": "What investment strategies work best for long-term growth?",
            "Portfolio Tips": "How can I optimize my portfolio to reduce risk?",
            "Market Trends": "What market trends should I be aware of and following?"
        }
        
        self.input_field.setText(quick_question_prompts.get(question, question))
        self.input_field.setFocus()
    
    # In AiChatView class:
    def handle_send_click(self):
        """Handle send button click event - only add message to UI once"""
        text = self.input_field.text().strip()
        if text:
            # Add message to UI here ONLY
            # Signal to the presenter
            self.send_message_requested.emit(text)
            self.input_field.clear()
            self.set_typing_indicator(True)

    # Make sure AI responses correctly use from_user=False
    def add_message(self, message, from_user=True):
        message_container = QFrame()
        message_container.setStyleSheet("background: transparent;")
        
        message_layout = QHBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setTextFormat(Qt.AutoText)
        bubble.setMaximumWidth(500)
        
        # Ensure different styling for user vs AI
        if from_user:
            # User message - yellow bubble, right aligned
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #F0B90B;
                    color: black;
                    padding: 12px 18px;
                    border-radius: 18px;
                    font-size: 14px;
                }
            """)
            
            user_icon = QLabel("👤")
            user_icon.setStyleSheet("""
                QLabel {
                    background-color: #2A2D35;
                    border-radius: 15px;
                    min-width: 30px;
                    min-height: 30px;
                    max-width: 30px;
                    max-height: 30px;
                    font-size: 13px;
                    padding-top: 3px;
                    text-align: center;
                }
            """)
            
            # Right alignment
            message_layout.addStretch()
            message_layout.addWidget(bubble)
            message_layout.addWidget(user_icon)
        else:
            # AI message - grey bubble, left aligned
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #2A2D35;
                    color: white;
                    padding: 12px 18px;
                    border-radius: 18px;
                    font-size: 14px;
                    line-height: 1.4;
                }
            """)
            
            ai_icon = QLabel("🤖")
            ai_icon.setStyleSheet("""
                QLabel {
                    background-color: #2A2D35;
                    border-radius: 15px;
                    min-width: 30px;
                    min-height: 30px;
                    max-width: 30px;
                    max-height: 30px;
                    font-size: 13px;
                    padding-top: 3px;
                    text-align: center;
                }
            """)
            
            # Left alignment
            message_layout.addWidget(ai_icon)
            message_layout.addWidget(bubble)
            message_layout.addStretch()
        
        self.chat_layout.addWidget(message_container)
        QTimer.singleShot(100, self.scroll_to_bottom)

        
    def set_typing_indicator(self, visible: bool):
        """Shows or hides a typing indicator"""
        if visible:
            if not hasattr(self, '_typing_container') or self._typing_container is None:
                self._typing_container = QFrame()
                self._typing_container.setStyleSheet("background: transparent;")
                
                typing_layout = QHBoxLayout(self._typing_container)
                typing_layout.setContentsMargins(0, 0, 0, 0)
                
                # AI icon
                ai_icon = QLabel("🤖")
                ai_icon.setStyleSheet("""
                    QLabel {
                        background-color: #2A2D35;
                        border-radius: 15px;
                        min-width: 30px;
                        min-height: 30px;
                        max-width: 30px;
                        max-height: 30px;
                        font-size: 13px;
                        padding-top: 3px;
                        text-align: center;
                    }
                """)
                
                # Typing indicator with animation effect
                self._typing_label = QLabel("Thinking...")
                self._typing_label.setStyleSheet("""
                    QLabel {
                        background-color: #2A2D35;
                        color: #BBBBBB;
                        padding: 12px 18px;
                        border-radius: 18px;
                        font-size: 14px;
                    }
                """)
                
                typing_layout.addWidget(ai_icon)
                typing_layout.addWidget(self._typing_label)
                typing_layout.addStretch()
            
            # Remove if already in layout
            if self._typing_container.parent() is not None:
                self.chat_layout.removeWidget(self._typing_container)
            
            # Add to bottom of chat
            self.chat_layout.addWidget(self._typing_container)
            self._typing_container.show()
            
            # Start typing animation
            self.animate_typing()
            
            # Scroll to show typing indicator
            self.scroll_to_bottom()
        else:
            # Hide typing indicator
            if hasattr(self, '_typing_container') and self._typing_container:
                self.chat_layout.removeWidget(self._typing_container)
                self._typing_container.hide()
    
    def animate_typing(self):
        """Animate the typing dots"""
        if hasattr(self, '_typing_label') and self._typing_label:
            current_text = self._typing_label.text()
            
            if current_text == "Thinking...":
                self._typing_label.setText("Thinking.")
            elif current_text == "Thinking.":
                self._typing_label.setText("Thinking..")
            elif current_text == "Thinking..":
                self._typing_label.setText("Thinking...")
            else:
                self._typing_label.setText("Thinking.")
            
            # Continue animation while visible
            if self._typing_container.isVisible():
                QTimer.singleShot(500, self.animate_typing)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat area"""
        vertical_bar = self.scroll_area.verticalScrollBar()
        vertical_bar.setValue(vertical_bar.maximum())