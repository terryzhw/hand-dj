from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from tracking.dj_controller import DJController
from audio.youtube_audio import YouTubeAudio
from gui.styles import *
from gui.base_page import BasePage
import os


class PlayPage(BasePage):
    def __init__(self, on_back_callback, on_play_callback=None):
        super().__init__(on_back_callback, "Play")
        self.on_play_callback = on_play_callback

    def setup_content(self, layout):
        instructions = QLabel("Insert YouTube Link")
        instructions.setFont(QFont("Arial", SUBTITLE_FONT_SIZE))
        instructions.setAlignment(Qt.AlignCenter)

        self.youtube_link_input = QLineEdit()
        self.youtube_link_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.youtube_link_input.setFont(QFont("Arial", INPUT_FONT_SIZE))
        self.youtube_link_input.setStyleSheet(INPUT_STYLE)

        run_btn = QPushButton("Run")
        run_btn.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        run_btn.setStyleSheet(BUTTON_STYLE)
        run_btn.clicked.connect(self.run_hand_dj)

        layout.insertWidget(1, instructions)
        layout.insertWidget(2, self.youtube_link_input)
        layout.insertWidget(3, run_btn)

    def run_hand_dj(self):
        youtube_url = self.youtube_link_input.text().strip()
        if not youtube_url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube link.")
            return

        audio_fetcher = YouTubeAudio()
        audio_data = audio_fetcher.fetch(youtube_url)
        video_title = audio_fetcher.video_title or "Unknown Song"

        temp_audio_file = "youtube_audio.wav"
        audio_data.export(temp_audio_file, format="wav")

        dj_controller = DJController(audio_file=temp_audio_file)

        if self.on_play_callback:
            self.on_play_callback(video_title, dj_controller)

        dj_controller.run()

        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
