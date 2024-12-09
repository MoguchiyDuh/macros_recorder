from typing import Literal
import pygame


class SoundManager:
    def __init__(
        self,
        start_sound_path: str,
        stop_sound_path: str,
        start_recording_sound_path: str,
        stop_recording_sound_path: str,
    ):
        pygame.mixer.init()
        self.sounds_map = {
            "start_macro": pygame.mixer.Sound(start_sound_path),
            "stop_macro": pygame.mixer.Sound(stop_sound_path),
            "start_recording": pygame.mixer.Sound(start_recording_sound_path),
            "stop_recording": pygame.mixer.Sound(stop_recording_sound_path),
        }

    def play_sound(
        self,
        sound_name: Literal[
            "start_macro", "stop_macro", "start_recording", "stop_recording"
        ],
        volume: float = 1.0,
    ):
        sound = self.sounds_map.get(sound_name, None)
        if sound is not None:
            sound.set_volume(volume)
            pygame.mixer.Sound.play(sound)
        else:
            raise KeyError("Sound is not found")
