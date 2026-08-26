
import os
import pygame
import threading
import time
import tempfile
from pydub import AudioSegment


class PlaybackManager:
    def __init__(self, sample_rate, buffer_size):
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=buffer_size)
        pygame.mixer.init()

        self.is_playing = False
        self.current_position_ms = 0.0
        self.audio_length_ms = 0.0
        self.temp_files = []
        self.playback_thread = None
        self.stop_thread = False

    def play(self, audio, start_position_s=0.0):
        # pygame can only play from files, so we write to a temp file first
        temp_file = self.save_to_temp(audio)

        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play(start=start_position_s)

        self.is_playing = True
        self.audio_length_ms = len(audio)
        self.current_position_ms = start_position_s * 1000
        self.start_progress_tracking()
        return True

    def set_volume(self, volume):
        if self.is_playing:
            pygame.mixer.music.set_volume(volume)

    def pause(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.stop_thread = True

    def resume(self):
        if not self.is_playing and self.audio_length_ms > 0:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.start_progress_tracking()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_position_ms = 0.0
        self.stop_thread = True

    def get_current_position_s(self):
        return self.current_position_ms / 1000.0

    def save_to_temp(self, audio):
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav', prefix='hand_dj_temp_')
        os.close(temp_fd)
        audio.export(temp_path, format='wav')
        self.temp_files.append(temp_path)

        # don't let temp files pile up on disk
        while len(self.temp_files) > 2:
            old_file = self.temp_files.pop(0)
            if os.path.exists(old_file):
                os.unlink(old_file)

        return temp_path

    def start_progress_tracking(self):
        self.stop_thread = False
        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=self.track_progress, daemon=True)
            self.playback_thread.start()

    def track_progress(self):
        while self.is_playing and not self.stop_thread:
            if not pygame.mixer.music.get_busy():
                self.stop()
                break
            self.current_position_ms += 100
            time.sleep(0.1)

    def cleanup(self):
        self.stop()
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        self.temp_files.clear()
        pygame.mixer.quit()
