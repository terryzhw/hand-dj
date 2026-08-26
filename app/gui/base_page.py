from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from gui.styles import BACKGROUND_STYLE, TITLE_FONT_SIZE, BUTTON_FONT_SIZE, BUTTON_STYLE


class BasePage(QWidget):
    def __init__(self, on_back_callback, page_title):
        super().__init__()
        self.on_back_callback = on_back_callback
        self.page_title = page_title
        self.setStyleSheet(BACKGROUND_STYLE)
        self.create_base_page()

    def create_base_page(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        title = QLabel(self.page_title)
        title.setFont(QFont("Arial", TITLE_FONT_SIZE, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)
        self.main_layout.addStretch()

        self.setup_content(self.main_layout)

        self.main_layout.addStretch()

        back_btn = QPushButton("Back")
        back_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        back_btn.setStyleSheet(BUTTON_STYLE)
        back_btn.clicked.connect(self.on_back_callback)
        self.main_layout.addWidget(back_btn)

        self.setLayout(self.main_layout)

    def setup_content(self, layout):
        pass
