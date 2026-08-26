from PyQt5.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
from gui.base_page import BasePage


class InstructionsPage(BasePage):
    def __init__(self, on_back_callback):
        super().__init__(on_back_callback, "Instructions")

    def setup_content(self, layout):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        instructions_text = """
        <h2>Hand Controls</h2>
        <p><b>Pitch:</b> Left hand index/thumb up and down</p>
        <p><b>Volume:</b> Move hands apart or together</p>
        <p><b>Reverb:</b> Right hand index/thumb up and down</p>

        <h2>Tips</h2>
        <p>- Ensure your camera is connected and lighting is good</p>
        <p>- Keep hands visible and make smooth movements</p>
        """

        label = QLabel(instructions_text)
        label.setFont(QFont("Arial", 12))
        label.setWordWrap(True)
        label.setStyleSheet("color: white; padding: 10px;")

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.addWidget(label)
        content_widget.setLayout(content_layout)

        scroll_area.setWidget(content_widget)
        layout.insertWidget(1, scroll_area)
