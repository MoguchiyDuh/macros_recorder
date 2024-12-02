from time import time, sleep
from threading import Thread, Event
import win32api
import win32con
from keyboard import remove_hotkey, add_hotkey

from key_map import KEY_MAP
from config_manager import load_macro_list, update_macro_list


class MacroController:
    def __init__(self, update_time=0.01, min_delta_mouse_pos=30):
        self.recorded_macro_actions = []
        self.macros_list = load_macro_list()
        self.__stop_trigger = Event()
        self.__update_time = update_time
        self.__min_delta_mouse_pos = min_delta_mouse_pos

    # Macros DB Functions
    def add_macro(
        self,
        macro_name: str,
        hotkey: str | None = "",
        active: bool | None = False,
    ):
        macro = {
            "name": macro_name,
            "actions": self.recorded_macro_actions,
            "hotkey": hotkey,
            "active": active,
        }
        if macro_name not in [macro_name["name"] for macro_name in self.macros_list]:
            self.macros_list.append(macro)
            update_macro_list(self.macros_list)
        else:
            print(f"Macro with name {macro_name} already exists.")

    def update_macro(
        self,
        macro_name: str,
        new_macro_name: str | None = None,
        hotkey: str | None = None,
        is_active: bool | None = None,
    ):
        if hotkey is not None:
            self.macros_list[macro_name]["hotkey"] = hotkey
        if is_active is not None:
            self.macros_list[macro_name]["active"] = is_active
        if new_macro_name is not None:
            self.macros_list[new_macro_name] = self.macros_list.pop(macro_name)
        update_macro_list(self.macros_list)

    def delete_macro(self, macro_name: str):
        if macro_name in self.macros_list:
            del self.macros_list[macro_name]
            update_macro_list(self.macros_list)
        else:
            print(f"Macro {macro_name} is not found")

    def enable_macro(self, macro_name: str):
        add_hotkey(hotkey_or_callback=self.macros_list[macro_name]["hotkey"])
        self.update_macro(is_active=True)

    def disable_macro(self, macro_name: str):
        remove_hotkey(hotkey_or_callback=self.macros_list[macro_name]["hotkey"])
        self.update_macro(is_active=False)

    def enable_all(self):
        for macro in self.macros_list:
            self.enable_macro(macro["name"])

    def disable_all(self):
        for macro in self.macros_list:
            self.disable_macro(macro["name"])

    # Macro Recording
    def start_recording(self):
        self.recorded_macro_actions = []
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
