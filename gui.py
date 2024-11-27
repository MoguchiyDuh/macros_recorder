import json
import os
from PIL import Image
from colorama import Fore
import customtkinter as ctk
from popup_window import show_info_window, show_warning_window, show_error_window


# TODO:


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.load_theme_config()

        # GLOBAL VARS
        self.WINDOW_MIN_SIZE = (500, 500)

        self.title("Macros Recorder")
        self.minsize(*self.WINDOW_MIN_SIZE)
        self.iconbitmap(
            ctk.ThemeManager.theme["MacrosIcon"][self._get_appearance_mode()]
        )

        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def load_theme_config(self, theme_name: str = "main"):
        with open("./config.json", "r") as file:
            config: dict = json.load(file)
            theme_name = config.get("theme", "main")

        THEMES_DIR = "./assets/themes"
        theme_path = os.path.join(THEMES_DIR, theme_name + ".json")
        with open(theme_path, "r") as file:
            try:
                ctk.set_default_color_theme(theme_path)
            except Exception as e:
                ctk.set_default_color_theme("blue")
                print(f"Can't load custom theme, using default blue theme. {e}")

    def create_widgets(self):
        # PAGE MAIN

        # ROW 0
        self.btn_toggle = ctk.CTkButton(
            self,
            width=150,
            height=35,
            **ctk.ThemeManager.theme["MacrosButtonToggle"],
            text="Start",
            font=ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"]),
            command=None,
        )
        self.btn_toggle.grid(row=0, column=0, padx=10, pady=10)

        settings_icon_size = (30, 30)
        self.settings_icon = ctk.CTkImage(
            dark_image=Image.open(ctk.ThemeManager.theme["MacrosSettingsIcon"]["dark"]),
            light_image=Image.open(
                ctk.ThemeManager.theme["MacrosSettingsIcon"]["light"]
            ),
            size=settings_icon_size,
        )

        self.settings_icon_label = ctk.CTkButton(
            self,
            width=settings_icon_size[0],
            height=settings_icon_size[1],
            **ctk.ThemeManager.theme["MacrosIconButton"],
            text="",
            image=self.settings_icon,
            command=None,
        )
        self.settings_icon_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")


ctk.set_appearance_mode("dark")
root = App()
root.mainloop()

ctk.set_appearance_mode("light")
root2 = App()
root2.mainloop()
