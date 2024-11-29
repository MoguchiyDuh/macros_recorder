import json
from time import time, sleep
from threading import Thread, Event
from typing import Literal
import win32api
import win32con
import pygame
import os, sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from key_map import KEY_MAP


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


class MacroController:
    def __init__(self, update_time=0.01, min_delta_mouse_pos=30):
        self.recorded_macro = []
        self.macros_list = {}
        self.macro_active = False
        self.__stop_trigger = Event()
        self.__update_time = update_time
        self.__min_delta_mouse_pos = min_delta_mouse_pos

        # Loading macros list
        self.__load_macros_list()

    def __load_macros_list(self):
        file_name = "macros.json"
        try:
            if os.path.exists(file_name):
                with open(file_name, "r") as file:
                    self.macros_list = json.load(file)
            else:
                print("File is not found")
                self.macros_list = {}
                with open(file_name, "w") as file:
                    json.dump({}, file)
        except json.JSONDecodeError:
            self.macros_list = {}
            print("Couldn't load the macros list")

    def __update_macros_list(self):
        with open("./macros.json", "w") as file:
            json.dump(self.macros_list, file)

    # Macros DB Functions
    def add_macro(self, macro_name: str, macro_hotkey: str, active: bool):
        self.macros_list[macro_name] = {
            "macro": self.recorded_macro,
            "hotkey": macro_hotkey,
            "active": active,
        }
        self.__update_macros_list()

    def edit_macro(
        self,
        macro_name: str,
        new_macro_name: str,
        macro_hotkey: str | None = None,
        macro_toggle: bool | None = None,
    ):
        if new_macro_name is not None:
            self.macros_list[new_macro_name] = self.macros_list.pop(macro_name)
        if macro_hotkey is not None:
            self.macros_list[macro_name]["hotkey"] = macro_hotkey
        if macro_toggle == True:
            self.macros_list[macro_name]["active"] = not self.macros_list[macro_name][
                "active"
            ]
        self.__update_macros_list()

    def delete_macro(self, macro_name: str):
        del self.macros_list[macro_name]
        self.__update_macros_list()

    # Macro Recording
    def start_recording(self):
        self.recorded_macro = []
        thread = Thread(target=self.__record_macro)
        thread.daemon = True
        thread.start()

    def stop_recording(self):
        self.__stop_trigger.set()

    def __record_macro(self):
        key_states = {key: 0 for key in KEY_MAP}

        print("Listening for all keys. Press Ctrl+C to stop.")
        last_position = win32api.GetCursorPos()
        start_time = time()
        while not self.__stop_trigger.is_set():
            for key, vk_code in KEY_MAP.items():
                state = win32api.GetAsyncKeyState(vk_code)

                # Detect key press
                if state < 0 and key_states[key] == 0:
                    print(f"Key pressed: {key, time() - start_time}")
                    key_states[key] = 1
                    action_log = {
                        "type": "key_press",
                        "time": time() - start_time,
                        "key": key,
                    }
                    self.recorded_macro.append(action_log)

                # Detect key release
                elif state >= 0 and key_states[key] == 1:
                    print(f"Key released: {key, time() - start_time}")
                    key_states[key] = 0
                    action_log = {
                        "type": "key_release",
                        "time": time() - start_time,
                        "key": key,
                    }
                    self.recorded_macro.append(action_log)

                # Mouse movement detection
                current_position = win32api.GetCursorPos()

                d_position = (
                    abs(current_position[0] - last_position[0]) ** 2
                    + abs(current_position[1] - last_position[1]) ** 2
                ) ** 0.5

                # Don't log movement if less than delta
                if (
                    current_position != last_position
                    and d_position > self.__min_delta_mouse_pos
                ):
                    print(f"Mouse moved to: {current_position, time() - start_time}")
                    last_position = current_position
                    action_log = {
                        "type": "mouse_move",
                        "time": time() - start_time,
                        "pos": current_position,
                    }
                    self.recorded_macro.append(action_log)

            sleep(self.__update_time)  # Prevent high CPU usage

    # Macro Playback
    def play_macro(self, macro_name: str):
        action_list = self.macros_list.get(macro_name, None)
        if action_list:
            thread = Thread(target=self.__play_actions, args=(action_list))
            thread.daemon = True
            thread.start()
        else:
            raise NameError(f"Macro {macro_name} is not found")

    def __play_actions(self, macro: list):
        start_time = time()
        for action in macro:
            while time() - start_time < action["time"]:
                sleep(0.001)
            if action == "mouse_move":
                win32api.SetCursorPos(action["pos"])
            elif action == "key_press":
                vk_code = KEY_MAP.get(action["key"])
                if vk_code:
                    win32api.keybd_event(vk_code, 0, 0, 0)
            elif action == "key_release":
                vk_code = KEY_MAP.get(action["key"])
                if vk_code:
                    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            elif action == "scroll":
                pass
