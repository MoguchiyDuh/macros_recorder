from time import sleep
import customtkinter as ctk
from popup_window import show_info_window, show_warning_window, show_error_window


# TODO:
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Macros Recorder")
        self.iconbitmap(
            "./assets/icons/dark/icon.ico"
            if self._get_appearance_mode() == "dark"
            else "./assets/icons/light/icon.ico"
        )

        # GLOBAL VARS
        self.FONT = ("Roboto", 16)
        self.FONT_BOLD = ("Roboto", 16, "bond")

        self.create_widgets()

    def create_widgets(self):
        # PAGE MAIN

        # ROW 0
        self.btn_toggle = ctk.CTkButton(
            self,
            width=140,
            height=28,
            corner_radius=None,
            fg_color=None,
            hover_color=None,
            border_color=None,
            text="Start",
            font=self.FONT,
            command=None,
            compound="left",
        )
        self.btn_toggle.pack()


root = App()
root.mainloop()
