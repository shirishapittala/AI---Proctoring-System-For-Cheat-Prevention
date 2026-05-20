import sounddevice as sd
import numpy as np
from config import AUDIO_DEVICE, AUDIO_THRESHOLD

def detect_audio():
    try:
        audio = sd.rec(
            4096,
            samplerate=44100,
            channels=2,
            dtype="float32",
            device=AUDIO_DEVICE,
            blocking=True
        )

        audio = np.nan_to_num(audio)
        volume = np.sqrt(np.mean(audio ** 2))

        print("Audio volume:", volume)

        return volume > AUDIO_THRESHOLD

    except Exception as e:
        print("Audio error:", e)
        return False