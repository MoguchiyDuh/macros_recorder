import json
import tkinter as tk
from tkinter import messagebox, Listbox
from pynput import mouse, keyboard as pynput_keyboard
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
from threading import Thread
from keyboard import add_hotkey, remove_hotkey
from time import time, sleep
import pygame

# Config and Macros Storage
CONFIG_FILE = "./config.json"
MACROS_FILE = "./macros.json"
SOUND_START_FILE = "./assets/sounds/start_stop_sound.mp3"
SOUND_PLAY_FILE = "./assets/sounds/play_sound.mp3"

pygame.mixer.init()

# Load sounds
start_stop_sound = pygame.mixer.Sound(SOUND_START_FILE)
play_macro_sound = pygame.mixer.Sound(SOUND_PLAY_FILE)
start_stop_sound.set_volume(1)  # default sound volume - 100%
play_macro_sound.set_volume(1)  # default sound volume - 100%
sounds_map = {
    "start": start_stop_sound,
    "stop": start_stop_sound,
    "play": play_macro_sound,
}


def play_sound(sound_name):
    pygame.mixer.Sound.play(sounds_map.get(sound_name))


# Load configuration
def load_config():
    global CONFIG_FILE
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"start_hotkey": "ctrl+shift+s", "play_hotkey": "ctrl+shift+p"}


def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


# Load macros
def load_macros():
    global MACROS_FILE
    try:
        with open(MACROS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_macros(macros):
    global MACROS_FILE
    with open(MACROS_FILE, "w") as file:
        json.dump(macros, file, indent=4)


def delete_macro():
    global macros, selected_macro
    if selected_macro:
        del macros[selected_macro]
        save_macros(macros)
        update_macro_list()
    else:
        messagebox.showwarning("Warning", "No Marco Selected")


# Global Variables
macros = load_macros()
config = load_config()
current_macro = []
macro_active = False
start_time = None
pressed_keys = set()
selected_macro = None


# Macro Functions
def start_macro():
    global macro_active, current_macro, start_time
    if macro_active:
        return
    sleep(1)
    macro_active = True
    current_macro = []
    start_time = time()
    listener_thread = Thread(target=record_events)
    listener_thread.daemon = True
    listener_thread.start()
    play_sound("start")


def stop_macro():
    global macro_active, current_macro
    macro_active = False
    play_sound("stop")


def record_events():
    with pynput_keyboard.Listener(
        on_press=on_key_press, on_release=on_key_release
    ) as kb_listener, mouse.Listener(
        on_click=on_mouse_click, on_move=on_mouse_move, on_scroll=on_mouse_scroll
    ) as mouse_listener:
        kb_listener.join()
        mouse_listener.join()


def on_key_press(key):
    if macro_active:
        try:
            add_action(
                {"type": "key_press", "time": time() - start_time, "key": key.char}
            )
        except AttributeError:
            add_action(
                {"type": "key_press", "time": time() - start_time, "key": str(key)}
            )


def on_key_release(key):
    if macro_active:
        try:
            add_action(
                {"type": "key_release", "time": time() - start_time, "key": key.char}
            )
        except AttributeError:
            add_action(
                {"type": "key_release", "time": time() - start_time, "key": str(key)}
            )


def on_mouse_click(x, y, button, pressed):
    if macro_active:
        action = "mouse_press" if pressed else "mouse_release"
        add_action(
            {
                "type": action,
                "time": time() - start_time,
                "button": str(button),
                "x": x,
                "y": y,
            }
        )


def on_mouse_move(x, y):
    if macro_active:
        add_action({"type": "mouse_move", "time": time() - start_time, "x": x, "y": y})


def on_mouse_scroll(x, y, dx, dy):
    if macro_active:
        add_action(
            {
                "type": "mouse_scroll",
                "time": time() - start_time,
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
            }
        )


def add_action(action):
    current_macro.append(action)


# Playback Function
def play_macro(macro_name):
    global pressed_keys, macros
    pressed_keys = set()

    if macro_name not in macros:
        messagebox.showerror("Error", "Macro not found!")
        return

    sleep(1)
    play_sound("play")
    events = macros[macro_name]
    for i, event in enumerate(events):
        if i > 0:
            delay = event["time"] - events[i - 1]["time"]
            sleep(delay)
        play_event(event)

    for key in pressed_keys:
        play_event({"type": "key_release", "key": key})

    play_sound("play")


def resolve_key(key):
    if key is not None:
        if "Key" in key:
            return getattr(Key, key.split(".", 1)[1], None)
        elif "Button" in key:
            return getattr(Button, key.split(".", 1)[1], None)
        elif "<" in key:
            return KeyCode.from_scancode(key[1:-1])
        else:
            return key


def play_event(action):
    global pressed_keys
    controller_mouse = mouse.Controller()
    controller_keyboard = pynput_keyboard.Controller()

    if action["type"] == "mouse_move":
        controller_mouse.position = (action["x"], action["y"])

    elif action["type"] == "mouse_press":
        button = resolve_key(action["button"])
        if button:
            controller_mouse.press(button)

    elif action["type"] == "mouse_release":
        button = resolve_key(action["button"])
        if button:
            controller_mouse.release(button)

    elif action["type"] == "mouse_scroll":
        controller_mouse.position = (action["x"], action["y"])
        controller_mouse.scroll(action["dx"], action["dy"])

    elif action["type"] == "key_press":
        key = resolve_key(action["key"])
        if key:
            controller_keyboard.press(key)
            pressed_keys.add(action["key"])

    elif action["type"] == "key_release":
        key = resolve_key(action["key"])
        if key:
            controller_keyboard.release(key)


# GUI Functions
def save_macro(macro_name):
    global macros
    if not macro_name:
        messagebox.showerror("Error", "Macro name cannot be empty!")
        return
    macros[macro_name] = current_macro
    save_macros(macros)
    update_macro_list()
    messagebox.showinfo("Success", f"Macro '{macro_name}' saved successfully!")


def update_macro_list():
    global macros
    macro_list.delete(0, tk.END)
    for name in macros.keys():
        macro_list.insert(tk.END, name)


def select_macro(event):
    global selected_macro
    selected = macro_list.curselection()
    if selected:
        selected_macro = macro_list.get(selected[0])
        current_label.config(text=f"Current Macro: {selected_macro}")


# GUI Setup
root = tk.Tk()
root.title("Macros Recorder")

# Labels
current_label = tk.Label(root, text="Current Macro: None")
current_label.grid(row=0, column=0, columnspan=2)

# Start Macro Bind
start_label = tk.Label(root, text="Start Bind:")
start_label.grid(row=1, column=0)
start_entry = tk.Entry(root)
start_entry.insert(0, config["start_hotkey"])
start_entry.grid(row=1, column=1)
start_button = tk.Button(
    root, text="Set", command=lambda: set_bind("start_hotkey", start_entry.get())
)
start_button.grid(row=1, column=2)

# Play Macro Bind
play_label = tk.Label(root, text="Play Bind:")
play_label.grid(row=2, column=0)
play_entry = tk.Entry(root)
play_entry.insert(0, config["play_hotkey"])
play_entry.grid(row=2, column=1)
play_button = tk.Button(
    root, text="Set", command=lambda: set_bind("play_hotkey", play_entry.get())
)
play_button.grid(row=2, column=2)

# Save Macro
save_label = tk.Label(root, text="Macro Name:")
save_label.grid(row=3, column=0)
save_entry = tk.Entry(root)
save_entry.insert(0, "macro1")
save_entry.grid(row=3, column=1)
save_button = tk.Button(root, text="Save", command=lambda: save_macro(save_entry.get()))
save_button.grid(row=3, column=2)

# Macros List
list_label = tk.Label(root, text="Saved Macros:")
list_label.grid(row=4, column=0)
delete_macro_button = tk.Button(
    root,
    text="Delete Selected Macros",
    command=delete_macro,
)
delete_macro_button.grid(row=4, column=1)
macro_list = Listbox(root, height=10)
macro_list.grid(row=5, column=0, columnspan=2)
macro_list.bind("<<ListboxSelect>>", select_macro)


# Hotkey Functions
def set_bind(action, key_combination):
    remove_hotkey(config[action])
    config[action] = key_combination
    save_config(config)
    if action == "start_macro":
        add_hotkey(config["start_hotkey"], toggle_macro)
    elif action == "play_hotkey":
        add_hotkey(config["play_hotkey"], lambda: play_macro(selected_macro))
    messagebox.showinfo("Info", f"Bind {action} set to: {key_combination}")
    root.focus()


def toggle_macro():
    if macro_active:
        stop_macro()
    else:
        start_macro()


# Initialize Hotkeys
add_hotkey(config["start_hotkey"], toggle_macro)
add_hotkey(
    config["play_hotkey"],
    lambda: play_macro(selected_macro if "selected_macro" in globals() else None),
)

# Populate Macros List
update_macro_list()

# Start GUI Loop
root.mainloop()
