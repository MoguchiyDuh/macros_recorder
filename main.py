import json
import os
from time import sleep
from keyboard import add_hotkey, unhook_all
import customtkinter as ctk
import tkinter as tk
from PIL import Image

from new_logic import (
    SoundManager,
    MacroController,
)
from popup_window import PopupWindow


CONFIG_FILE_PATH = "./config.json"
THEME_PATH = "./assets/themes"

with open(CONFIG_FILE_PATH, "r") as file:
    CONFIG = json.load(file)


ctk.set_default_color_theme(os.path.join(THEME_PATH, CONFIG["theme"]) + ".json")
ctk.set_appearance_mode("dark" if CONFIG["dark_theme"] else "light")

mc = MacroController()
sm = SoundManager(
    CONFIG["start_sound_path"],
    CONFIG["stop_sound_path"],
    CONFIG["start_recording_sound_path"],
    CONFIG["stop_recording_sound_path"],
)

# Global Vars
ACTIVE_MODE = False
IS_RECORDING = False


def toggle_recording():
    global IS_RECORDING
    IS_RECORDING = not IS_RECORDING
    if IS_RECORDING:
        sleep(0.5)
        sm.play_sound("start_recording")
        mc.start_recording()
    else:
        sm.play_sound("stop_recording")
        mc.stop_recording()


def update_config(key: str, value: str):
    CONFIG[key] = value
    with open(CONFIG_FILE_PATH, "w") as file:
        json.dump(CONFIG, file, indent=4)


def bind_macros_hotkeys():
    pass


# Callbacks (Main Page)
def change_app_status_callback(status: bool):
    global toggle_button, toggle_button_var, ACTIVE_MODE
    if status:
        ACTIVE_MODE = True
        add_hotkey(hotkey=CONFIG["recording_hotkey"], callback=toggle_recording)
        bind_macros_hotkeys()
        toggle_button_var.set("Stop")
        toggle_button.configure(**ctk.ThemeManager.theme["MacrosToggleButton"]["stop"])
    else:
        ACTIVE_MODE = False
        unhook_all()
        toggle_button_var.set("Start")
        toggle_button.configure(**ctk.ThemeManager.theme["MacrosToggleButton"]["start"])


def settings_button_callback():
    global main_page
    change_app_status_callback(status=False)
    main_page.grid_forget()
    show_settings_page()


# Callbacks (Settings Page)
def recording_hotkey_set_callback(hotkey: str):
    global root
    root.focus()
    update_config("recording_hotkey", hotkey)
    pw = PopupWindow(root)
    pw.show_info_window(text=f"Hotkey changed to: \n{hotkey}")


def change_mode_callback():
    global root, theme_select_button, dark_theme_icon, light_theme_icon
    CONFIG["dark_theme"] = not CONFIG["dark_theme"]
    update_config("dark_theme", CONFIG["dark_theme"])

    if CONFIG["dark_theme"]:
        ctk.set_appearance_mode("dark")
        root.iconbitmap(ctk.ThemeManager.theme["MacrosIcon"]["dark"])
        theme_select_button.configure(image=dark_theme_icon)
    else:
        ctk.set_appearance_mode("light")
        root.iconbitmap(ctk.ThemeManager.theme["MacrosIcon"]["light"])
        theme_select_button.configure(image=light_theme_icon)


def back_button_callback():
    global settings_page
    settings_page.grid_forget()
    show_main_page()


# GUI Vars
WINDOW_SIZE = (500, 400)
ICON_SIZE = (35, 35)
CTK_COLOR = ctk.ThemeManager.theme["CTk"]["fg_color"]

# GUI
root = ctk.CTk()
root.title("Macros Recorder")
root.iconbitmap(
    ctk.ThemeManager.theme["MacrosIcon"]["dark"]
    if CONFIG["dark_theme"]
    else ctk.ThemeManager.theme["MacrosIcon"]["light"]
)
root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
root.resizable(False, False)
root.grid_rowconfigure(index=0, weight=1)
root.grid_columnconfigure(index=0, weight=1)

# Icons
settings_icon = ctk.CTkImage(
    light_image=Image.open(ctk.ThemeManager.theme["MacrosSettingsIcon"]["light"]),
    dark_image=Image.open(ctk.ThemeManager.theme["MacrosSettingsIcon"]["dark"]),
    size=ICON_SIZE,
)
light_theme_icon = ctk.CTkImage(
    light_image=Image.open(ctk.ThemeManager.theme["MacrosSwitchThemeIcon"]["light"]),
    size=ICON_SIZE,
)
dark_theme_icon = ctk.CTkImage(
    dark_image=Image.open(ctk.ThemeManager.theme["MacrosSwitchThemeIcon"]["dark"]),
    size=ICON_SIZE,
)
back_icon = ctk.CTkImage(
    light_image=Image.open(ctk.ThemeManager.theme["MacrosBackIcon"]["light"]),
    dark_image=Image.open(ctk.ThemeManager.theme["MacrosBackIcon"]["dark"]),
    size=ICON_SIZE,
)
add_icon = ctk.CTkImage(
    light_image=Image.open(ctk.ThemeManager.theme["MacrosAddIcon"]["light"]),
    dark_image=Image.open(ctk.ThemeManager.theme["MacrosAddIcon"]["dark"]),
    size=ICON_SIZE,
)

# Main Page
main_page = ctk.CTkFrame(root, fg_color=CTK_COLOR)
main_page.grid_rowconfigure(index=0, weight=1)
main_page.grid_rowconfigure(index=1, weight=0)
main_page.grid_columnconfigure(index=0, weight=1)
main_page.grid_columnconfigure(index=1, weight=2)

# Frames - 4 sections
macros_frame = ctk.CTkScrollableFrame(main_page, width=100)

info_frame = ctk.CTkFrame(main_page)

invis_frame = ctk.CTkFrame(main_page, height=30, fg_color=CTK_COLOR)
invis_frame.grid_rowconfigure(index=0, weight=1)
invis_frame.grid_columnconfigure(index=0, weight=1)
invis_frame.grid_columnconfigure(index=1, weight=1)

invis_frame2 = ctk.CTkFrame(main_page, height=30, fg_color=CTK_COLOR)
invis_frame2.grid_rowconfigure(index=0, weight=1)
invis_frame2.grid_columnconfigure(index=0, weight=1)
invis_frame2.grid_columnconfigure(index=1, weight=1)

# Invis Frame (bottom left) Buttons
settings_button = ctk.CTkButton(
    invis_frame,
    width=ICON_SIZE[0],
    height=ICON_SIZE[1],
    **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
    text="",
    image=settings_icon,
    command=settings_button_callback,
)

add_macro_button = ctk.CTkButton(
    invis_frame,
    width=ICON_SIZE[0],
    height=ICON_SIZE[1],
    **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
    text="",
    image=add_icon,
)

# Invis Frame (bottom right) Buttons
toggle_button_var = tk.StringVar(value="Start")
toggle_button = ctk.CTkButton(
    invis_frame2,
    **ctk.ThemeManager.theme["MacrosToggleButton"]["start"],
    font=ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"]),
    command=lambda: change_app_status_callback(toggle_button_var.get() == "Start"),
    textvariable=toggle_button_var,
)


# Settings Page
settings_page = ctk.CTkFrame(root, fg_color=CTK_COLOR)
# settings_page.grid_rowconfigure(0, weight=1)
# settings_page.grid_rowconfigure(1, weight=1)
settings_page.grid_columnconfigure(0, weight=1)

# Frames
theme_frame = ctk.CTkFrame(settings_page, height=50, fg_color=CTK_COLOR)
theme_frame.grid_rowconfigure(0, weight=1)
theme_frame.grid_columnconfigure(0, weight=1)

recording_hotkey_frame = ctk.CTkFrame(settings_page, height=50, fg_color=CTK_COLOR)
recording_hotkey_frame.grid_rowconfigure(0, weight=1)
recording_hotkey_frame.grid_columnconfigure(0, weight=1)

# Back Button
back_button = ctk.CTkButton(
    settings_page,
    width=ICON_SIZE[0],
    height=ICON_SIZE[1],
    **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
    text="",
    image=back_icon,
    command=back_button_callback,
)

# Theme Select Row
theme_select_label = ctk.CTkLabel(
    theme_frame,
    text="Current theme:",
    font=ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"]),
)

theme_select_button = ctk.CTkButton(
    theme_frame,
    width=ICON_SIZE[0],
    height=ICON_SIZE[1],
    **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
    text="",
    image=dark_theme_icon if CONFIG["dark_theme"] else light_theme_icon,
    command=change_mode_callback,
)

# Recording Hotkey Change Row
recording_hotkey_label = ctk.CTkLabel(
    recording_hotkey_frame,
    text="Recording hotkey:",
    font=ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"]),
)

recording_hotkey_entry = ctk.CTkEntry(recording_hotkey_frame, width=100)
recording_hotkey_entry.insert(0, CONFIG["recording_hotkey"])

recording_hotkey_set_button = ctk.CTkButton(
    recording_hotkey_frame,
    width=50,
    text="Set",
    font=ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"]),
    command=lambda: recording_hotkey_set_callback(recording_hotkey_entry.get()),
)


# Page Management
def show_main_page():
    global main_page, macros_frame, info_frame, invis_frame, invis_frame2, settings_button, add_macro_button, toggle_button
    main_page.grid(row=0, column=0, sticky="nsew")
    macros_frame.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="nsew")
    info_frame.grid(row=0, column=1, padx=(5, 10), pady=(10, 5), sticky="nsew")
    invis_frame.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew")
    invis_frame2.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nsew")
    settings_button.grid(row=0, column=0)
    add_macro_button.grid(row=0, column=1)
    toggle_button.grid(row=0, column=0, sticky="ns")


# Settings Page TODO: fix padding and grid
def show_settings_page():
    global main_page
    settings_page.grid(row=0, column=0, sticky="nsew")
    back_button.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
    theme_frame.grid(row=1, column=0, padx=10, pady=5)
    recording_hotkey_frame.grid(row=2, column=0, padx=10, pady=5)
    theme_select_label.grid(row=0, column=0, padx=(0, 10))
    theme_select_button.grid(row=0, column=1)
    recording_hotkey_label.grid(row=0, column=0)
    recording_hotkey_entry.grid(row=0, column=1, padx=10)
    recording_hotkey_set_button.grid(row=0, column=2)


show_main_page()

root.mainloop()
