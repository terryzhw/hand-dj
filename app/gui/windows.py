from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
from gui.instructions_page import InstructionsPage
from gui.play_page import PlayPage
from gui.control_page import ControlPage
from gui.styles import BACKGROUND_STYLE
from gui.main_page import MainPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dj_controller = None

        self.setWindowTitle("HandDJ")
        self.setGeometry(300, 100, 500, 600)
        self.setWindowIcon(QIcon("HandDJ.png"))
        self.setStyleSheet(BACKGROUND_STYLE)

        self.page_stack = QStackedWidget()
        self.setCentralWidget(self.page_stack)

        self.main_page = MainPage(
            on_play_callback=lambda: self.page_stack.setCurrentWidget(self.play_page),
            on_instructions_callback=lambda: self.page_stack.setCurrentWidget(self.instructions_page)
        )
        self.instructions_page = InstructionsPage(
            on_back_callback=lambda: self.page_stack.setCurrentWidget(self.main_page)
        )
        self.play_page = PlayPage(
            on_back_callback=lambda: self.page_stack.setCurrentWidget(self.main_page),
            on_play_callback=self.navigate_to_stats_page
        )
        self.stats_page = ControlPage(
            on_back_callback=lambda: self.page_stack.setCurrentWidget(self.main_page),
            overlay=None
        )

        self.page_stack.addWidget(self.main_page)
        self.page_stack.addWidget(self.instructions_page)
        self.page_stack.addWidget(self.play_page)
        self.page_stack.addWidget(self.stats_page)
        self.page_stack.setCurrentWidget(self.main_page)

    def navigate_to_stats_page(self, song_title=None, dj_controller=None):
        if song_title:
            self.stats_page.audio_file_name = song_title
            self.stats_page.song_title_label.setText(f"♪ {song_title}")

        if dj_controller:
            self.dj_controller = dj_controller
            self.stats_page.overlay = dj_controller

        self.page_stack.setCurrentWidget(self.stats_page)
