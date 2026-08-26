from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from gui.styles import BUTTON_FONT_SIZE, BUTTON_STYLE


class MainPage(QWidget):
    def __init__(self, on_play_callback, on_instructions_callback):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Menu")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        play_btn = QPushButton("Play")
        play_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        play_btn.setStyleSheet(BUTTON_STYLE)
        play_btn.clicked.connect(on_play_callback)

        instructions_btn = QPushButton("Instructions")
        instructions_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        instructions_btn.setStyleSheet(BUTTON_STYLE)
        instructions_btn.clicked.connect(on_instructions_callback)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(play_btn)
        layout.addWidget(instructions_btn)
        layout.addStretch()

        self.setLayout(layout)
