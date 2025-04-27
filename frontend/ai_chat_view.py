from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea
from PySide6.QtCore import Qt, Signal

# Don't inherit from IAiChatView!!
from interfaces import IAiChatView  

class AiChatView(QWidget):  # Only QWidget
    send_message_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


    def setup_ui(self):
        self.setWindowTitle("AI Investment Assistant")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #12141A; color: white;")

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: #1E2026;
                border: none;
            }
        """)
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_content)

        main_layout.addWidget(self.scroll_area)

        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your question...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2A2D35;
                border: 1px solid #F0B90B;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: white;
            }
        """)

        send_button = QPushButton("Send")
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #F0B90B;
                color: black;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F8C032;
            }
        """)
        send_button.clicked.connect(self.handle_send_click)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)

        main_layout.addLayout(input_layout)

    def handle_send_click(self):
        text = self.input_field.text().strip()
        if text:
            self.send_message_requested.emit(text)
            self.input_field.clear()

    def add_message(self, message, from_user=True):
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(400)

        if from_user:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #F0B90B;
                    color: black;
                    padding: 10px;
                    border-radius: 8px;
                    font-size: 14px;
                }
            """)
            bubble.setAlignment(Qt.AlignRight)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background-color: #2A2D35;
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                    font-size: 14px;
                }
            """)
            bubble.setAlignment(Qt.AlignLeft)

        self.chat_layout.addWidget(bubble)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())


    def set_typing_indicator(self, visible: bool):
        """Shows or hides a typing indicator like 'AI is typing...' always at the end."""
        if visible:
            if not hasattr(self, '_typing_label') or self._typing_label is None:
                self._typing_label = QLabel("🤖 AI is thinking...")
                self._typing_label.setStyleSheet("""
                    QLabel {
                        background-color: #2A2D35;
                        color: #F0B90B;
                        padding: 8px 12px;
                        border-radius: 10px;
                        font-size: 13px;
                    }
                """)
                self._typing_label.setAlignment(Qt.AlignLeft)

            # Always move typing label to the bottom
            if self._typing_label.parent() is not None:
                self.chat_layout.removeWidget(self._typing_label)
            self.chat_layout.addWidget(self._typing_label)

            self._typing_label.show()
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

        else:
            if hasattr(self, '_typing_label') and self._typing_label:
                self.chat_layout.removeWidget(self._typing_label)
                self._typing_label.hide()
