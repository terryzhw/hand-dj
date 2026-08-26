import sys
import os
import platform
from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QWidget, QPushButton,
    QHBoxLayout, QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from gui.base_page import BasePage
from gui.styles import BUTTON_FONT_SIZE, BUTTON_STYLE, SUBTITLE_FONT_SIZE, TITLE_FONT_SIZE


class ControlPage(BasePage):
    def __init__(self, on_back_callback, overlay=None, audio_file_name=None):
        self.overlay = overlay
        self.audio_file_name = audio_file_name or "Unknown Song"
        self._update_counter = 0

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        # macOS gui locks up if we poll too fast
        update_interval = 300 if platform.system() == 'Darwin' else 100
        self.update_timer.start(update_interval)

        super().__init__(on_back_callback, "Controller")

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

        self.setLayout(self.main_layout)

    def setup_content(self, layout):
        self.song_title_label = QLabel(f"♪ {self.audio_file_name}")
        self.song_title_label.setFont(QFont("Arial", SUBTITLE_FONT_SIZE, QFont.Bold))
        self.song_title_label.setAlignment(Qt.AlignCenter)
        self.song_title_label.setStyleSheet("color: #4CAF50; padding: 5px;")

        self.stats_label = QLabel(self.generate_stats_text())
        self.stats_label.setFont(QFont("Arial", 12))
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("color: white; padding: 10px;")

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.reset_button.setStyleSheet(BUTTON_STYLE)
        self.reset_button.clicked.connect(self.reset_audio_params)

        self.toggle_button = QPushButton("Play/Pause")
        self.toggle_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.toggle_button.setStyleSheet(BUTTON_STYLE)
        self.toggle_button.clicked.connect(self.toggle_playback)

        self.quit_button = QPushButton("Quit")
        self.quit_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.quit_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f44336; }
            QPushButton:pressed { background-color: #b71c1c; }
        """)
        self.quit_button.clicked.connect(self.quit_handdj)

        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.quit_button)

        toggles_layout = QHBoxLayout()
        toggles_layout.setSpacing(10)

        self.pitch_toggle_button = QPushButton("Pitch: On")
        self.pitch_toggle_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.pitch_toggle_button.setStyleSheet(BUTTON_STYLE)
        self.pitch_toggle_button.clicked.connect(lambda: self.toggle_control('pitch'))

        self.volume_toggle_button = QPushButton("Volume: On")
        self.volume_toggle_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.volume_toggle_button.setStyleSheet(BUTTON_STYLE)
        self.volume_toggle_button.clicked.connect(lambda: self.toggle_control('volume'))

        self.reverb_toggle_button = QPushButton("Reverb: On")
        self.reverb_toggle_button.setFont(QFont("Arial", BUTTON_FONT_SIZE))
        self.reverb_toggle_button.setStyleSheet(BUTTON_STYLE)
        self.reverb_toggle_button.clicked.connect(lambda: self.toggle_control('reverb'))

        toggles_layout.addWidget(self.pitch_toggle_button)
        toggles_layout.addWidget(self.volume_toggle_button)
        toggles_layout.addWidget(self.reverb_toggle_button)

        layout.insertWidget(1, self.song_title_label)
        layout.insertWidget(2, self.stats_label)

        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        controls_layout.addLayout(buttons_layout)
        controls_layout.addLayout(toggles_layout)
        controls_widget.setLayout(controls_layout)
        layout.insertWidget(3, controls_widget)

    def generate_stats_text(self):
        if not self.overlay:
            return """
            <h2>Waiting for Audio...</h2>
            <p style='color: #90CAF9; text-align: center; font-style: italic;'>
                Please start playing a song to see real-time statistics.
            </p>
            """

        stats = self.overlay.get_stats()
        off_tag = "<span style='color:#9e9e9e;'> (Disabled)</span>"

        is_playing = self.overlay.audio_controller.audio_processor.is_playing
        status = "Playing" if is_playing else "Paused"
        status_color = "#4CAF50" if is_playing else "#FF5722"

        pitch_on = self.overlay.is_control_enabled('pitch')
        reverb_on = self.overlay.is_control_enabled('reverb')
        volume_on = self.overlay.is_control_enabled('volume')

        return f"""
        <h2>Audio Statistics</h2>
        <table style="width: 100%; color: white; border-spacing: 10px;">
            <tr>
                <td><b>Status:</b></td>
                <td style="color: {status_color};">{status}</td>
            </tr>
            <tr>
                <td style="width: 50%;"><b>Pitch:</b></td>
                <td style="color: #4CAF50;">{stats['pitch']:.2f}x{'' if pitch_on else off_tag}</td>
            </tr>
            <tr>
                <td><b>Volume:</b></td>
                <td style="color: #2196F3;">{stats['volume']:.2f} ({stats['volume'] * 100:.0f}%){'' if volume_on else off_tag}</td>
            </tr>
            <tr>
                <td><b>Reverb:</b></td>
                <td style="color: #FF9800;">{stats['reverb']:.2f}{'' if reverb_on else off_tag}</td>
            </tr>
        </table>
        """

    def update_stats(self):
        self.stats_label.setText(self.generate_stats_text())
        self._update_counter += 1
        # button text updates are cheaper to skip, so only do it every 3rd tick
        if self._update_counter % 3 == 0:
            self.update_toggle_buttons()

    def update_toggle_buttons(self):
        has_overlay = bool(self.overlay)
        for btn in [self.pitch_toggle_button, self.volume_toggle_button, self.reverb_toggle_button]:
            btn.setEnabled(has_overlay)
        if not has_overlay:
            return
        self.pitch_toggle_button.setText(f"Pitch: {'On' if self.overlay.is_control_enabled('pitch') else 'Off'}")
        self.volume_toggle_button.setText(f"Volume: {'On' if self.overlay.is_control_enabled('volume') else 'Off'}")
        self.reverb_toggle_button.setText(f"Reverb: {'On' if self.overlay.is_control_enabled('reverb') else 'Off'}")

    def toggle_control(self, name):
        if not self.overlay:
            return
        # flush pending qt events so the button click doesn't feel laggy
        QApplication.processEvents()
        self.overlay.toggle_control(name)
        self.update_toggle_buttons()

    def reset_audio_params(self):
        if self.overlay:
            QApplication.processEvents()
            self.overlay.audio_controller.reset_parameters()

    def toggle_playback(self):
        if self.overlay:
            QApplication.processEvents()
            self.overlay.audio_controller.toggle_playback()

    def quit_handdj(self):
        reply = QMessageBox.question(
            self, "Quit", "Are you sure you want to quit",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.overlay:
                self.overlay.cleanup()

            temp_audio_file = "youtube_audio.wav"
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)

            sys.exit(0)

    def closeEvent(self, event):
        self.update_timer.stop()
        super().closeEvent(event)
