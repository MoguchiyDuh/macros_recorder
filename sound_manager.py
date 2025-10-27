import os
import winsound
from threading import Thread
from typing import Literal


class SoundManager:
    def __init__(
        self,
        start_sound_path: str,
        stop_sound_path: str,
        start_recording_sound_path: str,
        stop_recording_sound_path: str,
    ):
        self.sounds_map = {
            "start_macro": start_sound_path,
            "stop_macro": stop_sound_path,
            "start_recording": start_recording_sound_path,
            "stop_recording": stop_recording_sound_path,
        }

    def play_sound(
        self,
        sound_name: Literal[
            "start_macro", "stop_macro", "start_recording", "stop_recording"
        ],
        volume: float = 0.5,
    ):
        sound_path = self.sounds_map.get(sound_name, None)
        if sound_path is not None and os.path.exists(sound_path):
            thread = Thread(target=self._play_sound_async, args=(sound_path,))
            thread.daemon = True
            thread.start()
        elif sound_path is None:
            raise KeyError("Sound is not found")

    def _play_sound_async(self, sound_path: str):
        """Play sound asynchronously using winsound"""
        try:
            if sound_path.endswith(".wav"):
                winsound.PlaySound(
                    sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
            else:
                # Fallback beep for non-wav files (mp3)
                winsound.Beep(800, 100)
        except Exception:
            pass
