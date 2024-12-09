import os
from time import time, sleep
import customtkinter as ctk
from threading import Thread, Event
from colorama import Fore
import win32api
import win32con
from keyboard import remove_hotkey, add_hotkey

from key_map import KEY_MAP, MOUSE_MAP
from config_manager import load_macro_list
from config_manager import edit_macro as edit_macro_cm
from config_manager import add_macro as add_macro_cm
from config_manager import delete_macro as delete_macro_cm

from sound_manager import SoundManager


class MacroController:
    def __init__(self, update_time=0.01, min_delta_mouse_pos=30):
        self.recorded_macro_actions = []
        self.macros_list = load_macro_list()
        self.__is_loop_trigger = Event()
        self.__update_time = update_time
        self.__min_delta_mouse_pos = min_delta_mouse_pos
        self.__active_macro = None

        self.sm = SoundManager(
            ctk.ThemeManager.theme["Sounds"]["play_macro_sound"],
            ctk.ThemeManager.theme["Sounds"]["finish_macro_sound"],
            ctk.ThemeManager.theme["Sounds"]["start_recording_sound"],
            ctk.ThemeManager.theme["Sounds"]["stop_recording_sound"],
        )

    def update_macro_list(self):
        self.macros_list = load_macro_list()

    # Macros DB Functions
    def add_macro(
        self,
        macro_name: str,
        actions: list[dict],
        hotkey: str | None = "",
        is_active: bool | None = False,
    ):
        macro = {
            "actions": actions,
            "hotkey": hotkey,
            "is_active": is_active,
        }
        if macro_name not in self.macros_list:
            self.macros_list[macro_name] = macro
            add_macro_cm(macro_name=macro_name, macro=macro)
        else:
            print(
                f"{Fore.RED}[ERROR]{Fore.RESET}: Macro with name {macro_name} already exists."
            )

    def edit_macro(
        self,
        macro_name: str,
        new_macro_name: str | None = None,
        hotkey: str | None = None,
        is_active: bool | None = None,
    ):
        if hotkey is not None:
            self.macros_list[macro_name]["hotkey"] = hotkey
            edit_macro_cm(macro_name=macro_name, macro=self.macros_list[macro_name])
        if is_active is not None:
            self.macros_list[macro_name]["is_active"] = is_active
            edit_macro_cm(macro_name=macro_name, macro=self.macros_list[macro_name])
        if new_macro_name is not None:
            old_path = os.path.join("./macros", macro_name + ".json")
            new_path = os.path.join("./macros", new_macro_name + ".json")
            try:
                os.rename(old_path, new_path)
            except FileExistsError:
                print(
                    f"{Fore.RED}[ERROR]{Fore.RESET}: File with this name already exists"
                )
                return "ERROR"
            self.macros_list[new_macro_name] = self.macros_list.pop(macro_name)

    def delete_macro(self, macro_name: str):
        if macro_name in self.macros_list:
            del self.macros_list[macro_name]
            delete_macro_cm(macro_name=macro_name)
        else:
            print(f"{Fore.RED}[ERROR]{Fore.RESET}: Macro {macro_name} is not found")

    def enable_macro(self, macro_name: str, is_loop: bool | None = None):
        try:
            add_hotkey(
                hotkey=self.macros_list[macro_name]["hotkey"],
                callback=lambda: self.play_macro(
                    macro_name=macro_name, is_loop=is_loop
                ),
            )
            self.edit_macro(macro_name=macro_name, is_active=True)
        except ValueError:
            print(
                f"{Fore.RED}[ERROR]{Fore.RESET}: Invalid hotkey for macro: {macro_name}"
            )

    def disable_macro(self, macro_name: str):
        try:
            remove_hotkey(hotkey_or_callback=self.macros_list[macro_name]["hotkey"])
        except KeyError:
            print(f"{Fore.YELLOW}[WARNING]{Fore.RESET}: Macro {macro_name} is inactive")
        self.edit_macro(macro_name=macro_name, is_active=False)

    # Macro Recording
    def start_recording(self):
        self.sm.play_sound("start_recording")
        self.recorded_macro_actions = []
        self.__stop_trigger = Event()
        thread = Thread(target=self.__record_macro)
        thread.start()

    def stop_recording(self):
        self.sm.play_sound("stop_recording")
        self.__stop_trigger.set()
        for i in (-2, -1):
            if self.recorded_macro_actions[i]["type"] == "key_press":
                del self.recorded_macro_actions[i]

    def __record_macro(self):
        key_states = {key: 0 for key in KEY_MAP}
        print("Listening for all keys.")
        last_position = win32api.GetCursorPos()
        start_time = time()
        while not self.__stop_trigger.is_set():
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
                self.recorded_macro_actions.append(action_log)

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
                    self.recorded_macro_actions.append(action_log)

                # Detect key release
                elif state >= 0 and key_states[key] == 1:
                    print(f"Key released: {key, time() - start_time}")
                    key_states[key] = 0
                    action_log = {
                        "type": "key_release",
                        "time": time() - start_time,
                        "key": key,
                    }
                    self.recorded_macro_actions.append(action_log)

            sleep(self.__update_time)  # Prevent high CPU usage

    # Macro Playback
    def play_macro(self, macro_name: str, is_loop: bool | None):
        self.sm.play_sound("start_macro")
        action_list = self.macros_list.get(macro_name, None).get("actions", None)
        if action_list is None:
            print(f"Macro {macro_name} is not found")
        elif self.__active_macro is None:
            print(f"{Fore.GREEN}[INFO]{Fore.RESET}: Playing macro {macro_name}...")
            self.__active_macro = macro_name
            thread = Thread(
                target=self.__play_actions,
                args=(
                    action_list,
                    is_loop,
                ),
            )
            thread.daemon = True
            thread.start()
        else:
            print(
                f"{Fore.YELLOW}[WARNING]{Fore.RESET}: Macro {macro_name} is already playing"
            )

    def stop_macro(self):
        if self.__active_macro is not None:
            self.is_loop_event.set()

    def __play_actions(self, actions: list, is_loop: bool | None):
        start_time = time()
        while True:
            for action in actions:
                while time() - start_time < action["time"]:
                    sleep(0.001)
                match action["type"]:
                    case "mouse_move":
                        win32api.SetCursorPos(action["pos"])
                    case "key_press":
                        key = KEY_MAP.get(action["key"])
                        if key:
                            if action["key"] in MOUSE_MAP.keys():
                                win32api.mouse_event(
                                    MOUSE_MAP[action["key"]]["down"],
                                    0,
                                    0,
                                    MOUSE_MAP[action["key"]]["flag"],
                                    0,
                                )
                            else:
                                win32api.keybd_event(key, 0, 0, 0)
                    case "key_release":
                        key = KEY_MAP.get(action["key"])
                        if key:
                            if action["key"] in MOUSE_MAP.keys():
                                win32api.mouse_event(
                                    MOUSE_MAP[action["key"]]["up"],
                                    0,
                                    0,
                                    MOUSE_MAP[action["key"]]["flag"],
                                    0,
                                )
                            else:
                                win32api.keybd_event(
                                    key, 0, win32con.KEYEVENTF_KEYUP, 0
                                )
                    # idk how to do the scroll tracking with win32api
                    case "scroll":
                        pass
                    case "print":
                        print(action["text"])

            if not is_loop or self.__is_loop_trigger.is_set():
                self.__active_macro = None
                self.sm.play_sound("stop_macro")
                break
