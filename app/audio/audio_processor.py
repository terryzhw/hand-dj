
import threading
import numpy as np
from pydub import AudioSegment
from audio.reverb_effect import ReverbEffect
from audio.playback_manager import PlaybackManager
from modules.constants import *


class AudioProcessor:
    def __init__(self, sample_rate=DEFAULT_SAMPLE_RATE, buffer_size=DEFAULT_BUFFER_SIZE):
        self.original_audio = None
        self.params = {'volume': DEFAULT_VOLUME, 'pitch': DEFAULT_PITCH, 'reverb': DEFAULT_REVERB}
        self.reverb_engine = ReverbEffect()
        self.playback_manager = PlaybackManager(sample_rate=sample_rate, buffer_size=buffer_size)
        self.parameter_lock = threading.Lock()
        self.effects_thread = None
        self.is_processing_effects = False

    def load_file(self, file_path):
        self.original_audio = AudioSegment.from_file(file_path)

    def set_param(self, name, value):
        with self.parameter_lock:
            self.params[name] = value
            # volume can be changed instantly through the mixer, everything else
            # needs the whole audio re-processed
            if name == 'volume':
                self.playback_manager.set_volume(value)
            elif self.playback_manager.is_playing:
                self.apply_effects_async()

    def set_params(self, new_params):
        with self.parameter_lock:
            self.params.update(new_params)

        if 'volume' in new_params:
            self.playback_manager.set_volume(self.params['volume'])

        if self.playback_manager.is_playing:
            self.apply_effects_async()

    def play(self, start_position_s=0.0):
        if self.original_audio is None:
            return False
        processed_audio = self.apply_effects(self.original_audio, self.params)
        return self.playback_manager.play(processed_audio, start_position_s)

    def apply_effects_async(self):
        # skip if already processing so we don't pile up threads
        if self.is_processing_effects or (self.effects_thread and self.effects_thread.is_alive()):
            return
        self.effects_thread = threading.Thread(target=self.run_effects, daemon=True)
        self.effects_thread.start()

    def run_effects(self):
        self.is_processing_effects = True
        current_pos_s = self.playback_manager.get_current_position_s()
        with self.parameter_lock:
            current_params = self.params.copy()
        processed_audio = self.apply_effects(self.original_audio, current_params)
        self.playback_manager.play(processed_audio, start_position_s=current_pos_s)
        self.is_processing_effects = False

    def apply_effects(self, audio, params):
        volume = params.get('volume', DEFAULT_VOLUME)
        pitch = params.get('pitch', DEFAULT_PITCH)
        reverb = params.get('reverb', DEFAULT_REVERB)

        processed = self.apply_volume(audio, volume)
        processed = self.apply_pitch(processed, pitch)
        processed = self.reverb_engine.apply(processed, reverb)
        return processed

    def apply_volume(self, audio, volume):
        if abs(volume - 1.0) < 0.001:
            return audio
        if volume > 0.001:
            db_change = 20 * np.log10(volume)
            db_change = np.clip(db_change, -60, 12)
            return audio + db_change
        return audio - 60

    def apply_pitch(self, audio, pitch):
        if abs(pitch - 1.0) < 0.001:
            return audio
        # tricking pydub into pitch shift by changing the frame rate then resampling back
        new_frame_rate = int(audio.frame_rate * pitch)
        pitched_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
        return pitched_audio.set_frame_rate(DEFAULT_SAMPLE_RATE)

    def cleanup(self):
        self.playback_manager.cleanup()

    @property
    def is_playing(self):
        return self.playback_manager.is_playing

    def pause(self):
        self.playback_manager.pause()

    def resume(self):
        self.playback_manager.resume()
