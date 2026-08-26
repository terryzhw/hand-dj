
import threading
import numpy as np
from pydub import AudioSegment
from pedalboard import Pedalboard, Gain, PitchShift, Reverb
from audio.playback_manager import PlaybackManager


class AudioProcessor:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.original_audio = None
        self.params = {'volume': 1.0, 'pitch': 1.0, 'reverb': 0.0}
        self.playback_manager = PlaybackManager(sample_rate=sample_rate, buffer_size=buffer_size)
        self.parameter_lock = threading.Lock()
        self.effects_thread = None
        self.is_processing_effects = False

    def load_file(self, file_path):
        self.original_audio = AudioSegment.from_file(file_path)

    def set_param(self, name, value):
        with self.parameter_lock:
            self.params[name] = value
            # volume goes straight to the mixer, but everything else needs a full re-render
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
        # don't pile up threads if we're already mid-render
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

    def make_volume_effect(self, volume):
        if abs(volume - 1.0) < 0.001:
            return None
        if volume > 0.001:
            db_change = float(np.clip(20 * np.log10(volume), -60, 12))
        else:
            db_change = -60.0
        return Gain(gain_db=db_change)

    def make_pitch_effect(self, pitch):
        if abs(pitch - 1.0) < 0.001:
            return None
        semitones = 12 * np.log2(pitch)
        return PitchShift(semitones=semitones)

    def make_reverb_effect(self, reverb_amount):
        if reverb_amount <= 0.0:
            return None
        room_size = min(1.0, reverb_amount / 2.0)
        wet_level = min(1.0, reverb_amount / 2.0)
        return Reverb(
            room_size=room_size,
            wet_level=wet_level,
            dry_level=1.0 - wet_level * 0.5,
            damping=0.5 + 0.3 * room_size,
            width=1.0,
        )

    def apply_effects(self, audio, params):
        effects = [
            self.make_volume_effect(params.get('volume', 1.0)),
            self.make_pitch_effect(params.get('pitch', 1.0)),
            self.make_reverb_effect(params.get('reverb', 0.0)),
        ]
        effects = [e for e in effects if e is not None]

        if not effects:
            return audio

        board = Pedalboard(effects)

        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        if audio.channels == 2:
            samples = samples.reshape((-1, 2)).T
        else:
            samples = samples.reshape(1, -1)

        processed = board(samples, audio.frame_rate)

        if audio.channels == 2:
            processed = processed.T
        else:
            processed = processed[0]

        processed = np.clip(processed, -1.0, 1.0)
        i16 = np.ascontiguousarray((processed * 32767.0).astype(np.int16))
        return audio._spawn(i16.tobytes())

    def cleanup(self):
        self.playback_manager.cleanup()

    @property
    def is_playing(self):
        return self.playback_manager.is_playing

    def pause(self):
        self.playback_manager.pause()

    def resume(self):
        self.playback_manager.resume()
