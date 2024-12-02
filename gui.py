import json
import os
import sys
from time import sleep
from typing import Literal
from colorama import Fore
import customtkinter as ctk
import tkinter as tk
from PIL import Image

from macros_manager import MacroController
from sound_manager import SoundManager

from config_manager import load_config, update_config, load_localization
from popup_window import PopupWindow


class App(ctk.CTk):
    def __init__(self, window_size: tuple[int], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ===============VARIABLES===============
        self.CONFIG = load_config()
        self.LOCALIZATION = load_localization(self.CONFIG["lang"])
        self.THEME_PATH = "./assets/themes"
        self.change_theme(theme=self.CONFIG["theme"], init=True)

        self.CTK_COLOR = ctk.ThemeManager.theme["CTk"]["fg_color"]
        self.FONTBOLD = ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"])
        self.selected_macro = None
        self.IS_RECORDING = False

        self.sm = SoundManager(
            ctk.ThemeManager.theme["Sounds"]["start_sound_path"],
            ctk.ThemeManager.theme["Sounds"]["stop_sound_path"],
            ctk.ThemeManager.theme["Sounds"]["start_recording_sound_path"],
            ctk.ThemeManager.theme["Sounds"]["stop_recording_sound_path"],
        )
        self.mc = MacroController()

        # ===============APP SETUP===============
        self.title("Macros Recorder")
        self.iconbitmap(ctk.ThemeManager.theme["Icons"]["MacrosIcon"])
        self.geometry(f"{window_size[0]}x{window_size[1]}")
        self.resizable(False, False)
        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)

        ICON_SIZE = (35, 35)
        # ===============ICONS===============
        self.settings_icon = ctk.CTkImage(
            light_image=Image.open(
                ctk.ThemeManager.theme["Icons"]["MacrosSettingsIcon"]
            ),
            dark_image=Image.open(
                ctk.ThemeManager.theme["Icons"]["MacrosSettingsIcon"]
            ),
            size=ICON_SIZE,
        )
        self.mode_icon = ctk.CTkImage(
            light_image=Image.open(
                ctk.ThemeManager.theme["Icons"]["MacrosSwitchModeIcon"]
            ),
            dark_image=Image.open(
                ctk.ThemeManager.theme["Icons"]["MacrosSwitchModeIcon"]
            ),
            size=ICON_SIZE,
        )
        self.back_icon = ctk.CTkImage(
            light_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosBackIcon"]),
            dark_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosBackIcon"]),
            size=ICON_SIZE,
        )
        self.add_icon = ctk.CTkImage(
            light_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosAddIcon"]),
            dark_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosAddIcon"]),
            size=ICON_SIZE,
        )
        self.discord_icon = ctk.CTkImage(
            light_image=Image.open(ctk.ThemeManager.theme["Icons"]["DiscordLogoIcon"]),
            dark_image=Image.open(ctk.ThemeManager.theme["Icons"]["DiscordLogoIcon"]),
            size=ICON_SIZE,
        )

        # ===============MAIN PAGE WIDGETS===============
        self.main_page = ctk.CTkFrame(self, fg_color=self.CTK_COLOR)
        self.main_page.grid_rowconfigure(index=0, weight=1)
        self.main_page.grid_rowconfigure(index=1, weight=0)
        self.main_page.grid_columnconfigure(index=0, weight=1)
        self.main_page.grid_columnconfigure(index=1, weight=2)

        # ----------Frames----------
        MACROS_LIST_WIDTH = 100
        self.scrollable_macros_list_frame = ctk.CTkScrollableFrame(
            self.main_page,
            width=MACROS_LIST_WIDTH,
        )

        self.info_frame = ctk.CTkFrame(self.main_page)

        INVIS_FRAME_HEIGHT = 30
        self.invis_frame = ctk.CTkFrame(
            self.main_page, height=INVIS_FRAME_HEIGHT, fg_color=self.CTK_COLOR
        )  # for settings and add buttons
        self.invis_frame.grid_rowconfigure(index=0, weight=1)
        self.invis_frame.grid_columnconfigure(index=0, weight=1)
        self.invis_frame.grid_columnconfigure(index=1, weight=1)

        self.invis_frame2 = ctk.CTkFrame(
            self.main_page, height=INVIS_FRAME_HEIGHT, fg_color=self.CTK_COLOR
        )  # for enable/disable, delete buttons
        self.invis_frame2.grid_rowconfigure(index=0, weight=1)
        self.invis_frame2.grid_columnconfigure(index=0, weight=1)
        self.invis_frame2.grid_columnconfigure(index=1, weight=1)

        # ----------Invis Frame 1 (bottom left) Widgets----------
        self.settings_button = ctk.CTkButton(
            self.invis_frame,
            width=ICON_SIZE[0],
            height=ICON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
            text="",
            image=self.settings_icon,
            command=self.show_settings_page,
        )

        self.add_macro_button = ctk.CTkButton(
            self.invis_frame,
            width=ICON_SIZE[0],
            height=ICON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
            text="",
            image=self.add_icon,
            command=self.add_button_callback,
        )

        BUTTON_SIZE = (100, 35)
        # ----------Invis Frame 2 (bottom right) Widgets----------
        self.toggle_status_var = tk.StringVar(value=self.LOCALIZATION["status_enable"])
        self.toggle_macro_status_button = ctk.CTkButton(
            self.invis_frame2,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosToggleActiveButton"]["enable"],
            font=self.FONTBOLD,
            command=lambda: self.change_status_callback(
                self.toggle_status_var.get() == self.LOCALIZATION["status_enable"]
            ),
            textvariable=self.toggle_status_var,
        )

        self.delete_macro_button = ctk.CTkButton(
            self.invis_frame2,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["delete_button"],
            font=self.FONTBOLD,
            command=lambda: self.delete_button_callback(self.selected_macro),
        )

        self.save_macro_button = ctk.CTkButton(
            self.invis_frame2,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["save_button"],
            font=self.FONTBOLD,
            state="disabled",
            command=lambda: self.save_button_callback(),
        )

        MACRO_BUTTON_SIZE = (80, 20)
        # ----------Macros List----------
        self.macros_list_buttons = []
        for macro in self.mc.macros_list:
            macro_select_button = ctk.CTkButton(
                self.scrollable_macros_list_frame,
                width=MACRO_BUTTON_SIZE[0],
                height=MACRO_BUTTON_SIZE[1],
                **ctk.ThemeManager.theme["MacrosListButton"],
                text=macro["name"],
                command=lambda: self.select_macro(macro["name"]),
            )
            self.macros_list_buttons.append(macro_select_button)

        # ===============SETTINGS PAGE WIDGETS===============
        self.settings_page = ctk.CTkFrame(self, fg_color=self.CTK_COLOR)
        # self.settings_page.grid_rowconfigure(index=0, weight=0)
        # self.settings_page.grid_rowconfigure(index=1, weight=1)
        # self.settings_page.grid_rowconfigure(index=2, weight=1)
        self.settings_page.grid_columnconfigure(index=0, weight=1)

        # ----------Back Button----------
        self.back_button = ctk.CTkButton(
            self.settings_page,
            width=ICON_SIZE[0],
            height=ICON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
            text="",
            image=self.back_icon,
            command=self.show_main_page,
        )

        # ----------Frames----------
        SETTINGS_FRAME_WIDTH = 400
        # SETTINGS_FRAME_HEIGHT = 0

        self.theme_frame = ctk.CTkFrame(
            self.settings_page,
            width=SETTINGS_FRAME_WIDTH,
            # height=SETTINGS_FRAME_HEIGHT,
        )
        self.theme_frame.grid_rowconfigure(index=0, weight=1)
        self.theme_frame.grid_columnconfigure(index=0, weight=1)
        self.theme_frame.grid_columnconfigure(index=1, weight=1)

        self.lang_frame = ctk.CTkFrame(
            self.settings_page,
            width=SETTINGS_FRAME_WIDTH,
            # height=SETTINGS_FRAME_HEIGHT,
        )
        self.lang_frame.grid_rowconfigure(0, weight=1)
        self.lang_frame.grid_columnconfigure(0, weight=1)
        self.lang_frame.grid_columnconfigure(1, weight=1)
        # ----------Select Theme Widgets----------
        self.select_theme_label = ctk.CTkLabel(
            self.theme_frame,
            text=self.LOCALIZATION["select_theme"],
            font=self.FONTBOLD,
        )
        self.themes_option_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=self.available_themes(),
            command=self.change_theme,
        )
        self.themes_option_menu.set(self.CONFIG["theme"])

        self.select_lang_label = ctk.CTkLabel(
            self.lang_frame,
            text=self.LOCALIZATION["select_lang"],
            font=self.FONTBOLD,
        )
        self.langs_option_menu = ctk.CTkOptionMenu(
            self.lang_frame,
            values=["eng", "rus"],
            command=self.change_lang,
        )
        self.langs_option_menu.set(self.CONFIG["lang"])

    # ===============FUNCTIONS===============
    def change_theme(self, theme: str | None = "dark", init: bool | None = False):
        ctk.set_default_color_theme(os.path.join(self.THEME_PATH, theme + ".json"))
        if init:
            return
        self.CONFIG["theme"] = theme
        update_config(self.CONFIG)
        # I'm lazy to update all widgets manualy, so.. just restart the app
        os.execv(sys.executable, ["python"] + sys.argv)

    def change_lang(self, lang: str):
        self.CONFIG["lang"] = lang
        self.LOCALIZATION = load_localization(lang=lang)
        update_config(self.CONFIG)

        self.delete_macro_button.configure(text=self.LOCALIZATION["delete_button"])
        self.save_macro_button.configure(text=self.LOCALIZATION["save_button"])
        self.select_theme_label.configure(text=self.LOCALIZATION["select_theme"])
        self.select_lang_label.configure(text=self.LOCALIZATION["select_lang"])

    def toggle_recording(self):
        IS_RECORDING = not self.IS_RECORDING
        if IS_RECORDING:
            sleep(0.5)
            self.sm.play_sound("start_recording")
            self.mc.start_recording()
        else:
            self.sm.play_sound("stop_recording")
            self.mc.stop_recording()

    def select_macro(self, macro_name: str):
        pass

    def available_themes(self):
        themes_list = []
        for root, dirs, files in os.walk(self.THEME_PATH):
            for file in files:
                theme_name, extension = os.path.splitext(file)
                if extension == ".json":
                    themes_list.append(theme_name)
        return themes_list

    # ===============PAGE MANAGEMENT===============
    def clear_frame(self, frame: ctk.CTkFrame | None = None):
        if frame is not None:
            for widget in frame.winfo_children():
                widget.grid_forget()
        else:
            for widget in self.winfo_children():
                widget.grid_forget()

    def show_main_page(self):
        self.clear_frame()
        self.main_page.grid(row=0, column=0, sticky="nsew")
        self.scrollable_macros_list_frame.grid(
            row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="nsew"
        )
        self.info_frame.grid(row=0, column=1, padx=(5, 10), pady=(10, 5), sticky="nsew")
        self.invis_frame.grid(
            row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew"
        )
        self.invis_frame2.grid(
            row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nsew"
        )
        self.settings_button.grid(row=0, column=0)
        self.add_macro_button.grid(row=0, column=1)

    def clear_macro_info_frame(self):
        self.clear_frame(frame=self.info_frame)
        self.clear_frame(frame=self.invis_frame2)

    def show_macro_info(self):
        self.clear_macro_info_frame()
        self.toggle_macro_status_button.grid(row=0, column=0)
        self.delete_macro_button.grid(row=0, column=1)

    def show_macro_list(self, selected_macro_name: str | None = None):
        self.clear_frame(frame=self.scrollable_macros_list_frame)
        for index, macro_select_button in enumerate(self.macros_list_buttons):
            if (
                selected_macro_name is not None
                and selected_macro_name == macro_select_button["name"]
            ):
                macro_select_button.configure()
            macro_select_button.grid(row=index, column=0, padx=5, pady=(5, 0))

    def show_settings_page(self):
        self.clear_frame()
        self.settings_page.grid(row=0, column=0, sticky="nsew")
        self.back_button.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.theme_frame.grid(row=1, column=0, padx=80, pady=(30, 0), sticky="nwe")
        self.lang_frame.grid(row=2, column=0, padx=80, pady=(10, 0), sticky="nwe")
        self.select_theme_label.grid(row=0, column=0, padx=10, pady=10)
        self.themes_option_menu.grid(row=0, column=1, padx=10, pady=10)
        self.select_lang_label.grid(row=0, column=0, padx=10, pady=10)
        self.langs_option_menu.grid(row=0, column=1, padx=10, pady=10)

    # ===============CALLBACKS===============
    # ----------Main Page----------
    def change_status_callback(self, status: bool):
        if status:  # if True - change from Enable to Disable state
            self.toggle_macro_status_button.configure(
                **ctk.ThemeManager.theme["MacrosToggleActiveButton"]["disable"]
            )
            self.toggle_status_var.set(value=self.LOCALIZATION["status_disable"])

            self.mc.enable_macro(self.selected_macro["name"])
        else:
            self.toggle_macro_status_button.configure(
                **ctk.ThemeManager.theme["MacrosToggleActiveButton"]["enable"]
            )
            self.toggle_status_var.set(value=self.LOCALIZATION["status_enable"])

            self.mc.disable_macro(self.selected_macro["name"])

    def delete_button_callback(self):
        self.selected_macro = None
        self.mc.delete_macro(self.selected_macro["name"])
        self.clear_macro_info_frame()
        self.show_macro_list()

    def add_button_callback(self):
        self.clear_frame(frame=self.info_frame)
        self.clear_frame(frame=self.invis_frame2)

    def save_button_callback(self, macro_name: str | None, hotkey: str | None):
        if macro_name is None or hotkey is None:
            print(f"{Fore.RED}[Error]{Fore.RESET}: Macro name or hotkey is None")
        else:
            self.mc.add_macro(macro_name=macro_name, hotkey=hotkey)
            print(f"{Fore.CYAN}[Info]{Fore.RESET}: Macro {macro_name} saved!")
            self.show_macro_list()
            self.clear_macro_info_frame()
            self.show_macro_info()

    def toggle_mode_button_callback(self):
        self.CONFIG["mode"] = "dark" if self.CONFIG["mode"] == "light" else "light"
        self.change_theme(mode=self.CONFIG["mode"])
        update_config(self.CONFIG)

    # ----------Settings Page----------
    def recording_hotkey_set_callback(self, hotkey: str):
        self.focus()
        update_config("recording_hotkey", hotkey)

        pw = PopupWindow(self)
        pw.show_info_window(text=f"Hotkey changed to: \n{hotkey}")

    def change_theme_callback(self, theme: str):
        self.CONFIG["theme"] = theme
        update_config(self.CONFIG)
        ctk.set_default_color_theme(
            os.path.join(self.THEME_PATH, self.CONFIG["dark_theme"]) + ".json"
        )
