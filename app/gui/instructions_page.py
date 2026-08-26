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
        <h1>How to Use HandDJ</h1>

        <h2>Getting Started</h2>
        <p>1. Make sure your camera is connected and working</p>
        <p>2. Position yourself so your hands are clearly visible to the camera</p>
        <p>3. Keep good lighting for better hand detection</p>

        <h2>Hand Controls</h2>
        <p><b>Pitch Control:</b> Move your left index/thumb finger up and down to change the pitch of your music</p>
        <p><b>Volume Control:</b> Move hands apart/close to each other to change volume</p>
        <p><b>Reverb Effects:</b> Move your right index/thumb finger up and down to change the reverb of your music</p>

        <h2>Using the App</h2>
        <p><b>Main Page:</b> Start here to access all features</p>
        <p><b>Play Page:</b> Load YouTube link to play audio</p>
        <p><b>Control Page:</b> Watch real-time statistics and access control buttons</p>

        <h2>Tips for Best Results</h2>
        <p>- Keep your hands steady for precise control</p>
        <p>- Make clear, non-sudden movements</p>
        <p>- If tracking stops working, check your camera and lighting</p>
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
