
import time
import threading
from audio.audio_processor import AudioProcessor

PARAMETER_UPDATE_INTERVAL = 0.5
SMOOTHING_FACTOR = 0.2
# lower factor here so volume feels snappier under hand movement
VOLUME_SMOOTHING_FACTOR = 0.1
BUFFER_SIZE = 5


class AudioController:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.pitch = 1.0
        self.volume = 1.0
        self.reverb = 0.0
        self.pitch_buffer = []
        self.volume_buffer = []
        self.reverb_buffer = []
        self.parameter_update_lock = threading.Lock()
        self.last_update_time = time.time()
        self.audio_loaded = False

    def load_audio(self, audio_file):
        self.audio_processor.load_file(audio_file)
        self.audio_processor.play()
        self.audio_loaded = True

    def smooth_pitch(self, pitch):
        self.pitch = self.smooth_value(pitch, self.pitch_buffer, self.pitch)
        self.update_parameters()

    def smooth_reverb(self, reverb):
        self.reverb = self.smooth_value(reverb, self.reverb_buffer, self.reverb)
        self.update_parameters()

    def smooth_volume(self, volume):
        self.volume = self.smooth_value(volume, self.volume_buffer, self.volume, VOLUME_SMOOTHING_FACTOR)
        if self.audio_loaded:
            self.audio_processor.set_param('volume', self.volume)

    def update_parameters(self):
        # pitch and reverb re-process the whole audio, so don't do it too often
        current_time = time.time()
        if current_time - self.last_update_time > PARAMETER_UPDATE_INTERVAL:
            with self.parameter_update_lock:
                if self.audio_loaded:
                    self.audio_processor.set_param('pitch', self.pitch)
                    self.audio_processor.set_param('reverb', self.reverb)
            self.last_update_time = current_time

    def smooth_value(self, new_value, buffer, current_value, smoothing_factor=SMOOTHING_FACTOR):
        buffer.append(new_value)
        if len(buffer) > BUFFER_SIZE:
            buffer.pop(0)
        avg_value = sum(buffer) / len(buffer)
        return current_value + smoothing_factor * (avg_value - current_value)

    def get_stats(self):
        return {"pitch": self.pitch, "reverb": self.reverb, "volume": self.volume}

    def reset_parameters(self):
        self.pitch = 1.0
        self.volume = 1.0
        self.reverb = 0.0
        self.pitch_buffer.clear()
        self.volume_buffer.clear()
        self.reverb_buffer.clear()
        if self.audio_loaded:
            self.audio_processor.set_params({'pitch': 1.0, 'reverb': 0.0, 'volume': 1.0})

    def toggle_playback(self):
        if not self.audio_loaded:
            return
        if self.audio_processor.is_playing:
            self.audio_processor.pause()
        else:
            self.audio_processor.resume()

    def cleanup(self):
        self.audio_processor.cleanup()
