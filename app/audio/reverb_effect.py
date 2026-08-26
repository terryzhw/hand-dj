
import numpy as np
from pedalboard import Reverb


class ReverbEffect:
    def __init__(self):
        pass

    def apply(self, audio, reverb_amount):
        if reverb_amount <= 0.0:
            return audio

        room_size = min(1.0, reverb_amount / 2.0)
        wet_level = min(1.0, reverb_amount / 2.0)
        damping = 0.5 + 0.3 * room_size

        reverb = Reverb(
            room_size=room_size,
            wet_level=wet_level,
            dry_level=1.0 - wet_level * 0.5,
            damping=damping,
            width=1.0,
        )

        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        if audio.channels == 2:
            samples = samples.reshape((-1, 2)).T
        else:
            samples = samples.reshape(1, -1)

        processed = reverb(samples, audio.frame_rate)

        if audio.channels == 2:
            processed = processed.T
        else:
            processed = processed[0]

        processed = np.clip(processed, -1.0, 1.0)
        i16 = np.ascontiguousarray((processed * 32767.0).astype(np.int16))
        return audio._spawn(i16.tobytes())
