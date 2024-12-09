import customtkinter as ctk
from PIL import Image


class PopupWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.__WINDOW_SIZE = (300, 150)
        self.__IMAGE_SIZE = (40, 40)
        self.__BTN_SIZE = (80, 28)

        self.geometry(f"{self.__WINDOW_SIZE[0]}x{self.__WINDOW_SIZE[1]}")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

    def __yes_callback(self, popup, result_var):
        result_var.set(True)
        popup.destroy()

    def __no_callback(self, popup, result_var):
        result_var.set(False)
        popup.destroy()

    def __show_popup(
        self,
        title: str,
        text: str,
        image_path: str,
        is_yes_no_popup: bool = False,
    ) -> None | bool:
        self.title(title)

        image = ctk.CTkImage(
            light_image=Image.open(image_path),
            dark_image=Image.open(image_path),
            size=self.__IMAGE_SIZE,
        )

        image_label = ctk.CTkLabel(
            self,
            text="",
            image=image,
        )
        image_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        text_label = ctk.CTkLabel(
            self,
            text=text,
            wraplength=150,
        )
        text_label.grid(row=0, column=1, padx=10, pady=(5, 10))

        frame = ctk.CTkFrame(self)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        result_var = ctk.BooleanVar(value=None)

        if is_yes_no_popup:
            no_button = ctk.CTkButton(
                frame,
                width=self.__BTN_SIZE[0],
                height=self.__BTN_SIZE[1],
                text="No",
                command=lambda: self.__no_callback(self, result_var),
            )
            no_button.grid(row=0, column=0, padx=5, pady=5)

            yes_button = ctk.CTkButton(
                frame,
                width=self.__BTN_SIZE[0],
                height=self.__BTN_SIZE[1],
                text="Yes",
                command=lambda: self.__yes_callback(self, result_var),
            )
            yes_button.grid(row=0, column=1, padx=5, pady=5)
        else:
            ok_button = ctk.CTkButton(
                frame,
                width=self.__BTN_SIZE[0],
                height=self.__BTN_SIZE[1],
                text="OK",
                command=self.destroy,
            )
            ok_button.grid(padx=5, pady=5, sticky="e")

        self.transient()
        self.grab_set()
        self.wait_window()
        return result_var.get()

    def show_info_window(self, text: str = ""):
        self.__show_popup(
            title="Info",
            text=text,
            image_path=ctk.ThemeManager.theme["Icons"]["MacrosInfoIcon"],
        )

    def show_warning_window(self, text: str = ""):
        self.__show_popup(
            title="Warning",
            text=text,
            image_path=ctk.ThemeManager.theme["Icons"]["MacrosWarningIcon"],
        )

    def show_error_window(self, text: str = ""):
        self.__show_popup(
            title="Error",
            text=text,
            image_path=ctk.ThemeManager.theme["Icons"]["MacrosErrorIcon"],
        )

    def show_yes_no_window(self, text: str = "") -> bool:
        return self.__show_popup(
            title="Confirm",
            text=text,
            image_path=ctk.ThemeManager.theme["Icons"]["MacroQuestionIcon"],
            is_yes_no_popup=True,
        )
