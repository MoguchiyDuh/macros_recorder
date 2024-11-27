import customtkinter as ctk
from PIL import Image

WINDOW_MIN_SIZE = (250, 130)

IMAGE_SIZE = (40, 40)

BTN_SIZE = (80, 28)


def show_popup_window(title: str, text: str, image_paths: tuple[str, str]):
    popup = ctk.CTkToplevel()
    popup.title(title)
    popup.minsize(*WINDOW_MIN_SIZE)

    popup.grid_rowconfigure(0, weight=2)
    popup.grid_rowconfigure(1, weight=1)
    popup.grid_columnconfigure(0, weight=1)

    image = ctk.CTkImage(
        dark_image=Image.open(image_paths[0]),
        light_image=Image.open(image_paths[1]),
        size=IMAGE_SIZE,
    )

    text_label = ctk.CTkLabel(
        popup,
        padx=10,
        text=text,
        font=ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"]),
        image=image,
        compound="left",
        wraplength=300,
    )
    text_label.grid(row=0, column=0, padx=10, pady=10)

    frame = ctk.CTkFrame(popup)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid(row=1, column=0, sticky="nsew")

    # Create OK button inside the frame
    ok_button = ctk.CTkButton(
        frame,
        width=BTN_SIZE[0],
        height=BTN_SIZE[1],
        **ctk.ThemeManager.theme["MacrosButtonPopup"],
        text="OK",
        command=popup.destroy,
    )
    ok_button.grid(padx=5, pady=5, sticky="e")  # Center button inside the frame

    popup.transient()
    popup.grab_set()
    popup.wait_window()


INFO_DARK_PATH = "./assets/icons/dark/info.png"
INFO_LIGHT_PATH = "./assets/icons/light/info.png"


def show_info_window(text: str):
    show_popup_window(
        title="Info", text=text, image_paths=(INFO_DARK_PATH, INFO_LIGHT_PATH)
    )


WARNING_DARK_PATH = "./assets/icons/dark/warning.png"
WARNING_LIGHT_PATH = "./assets/icons/light/warning.png"


def show_warning_window(text: str):
    show_popup_window(
        title="Warning", text=text, image_paths=(WARNING_DARK_PATH, WARNING_LIGHT_PATH)
    )


ERROR_DARK_PATH = "./assets/icons/dark/error.png"
ERROR_LIGHT_PATH = "./assets/icons/light/error.png"


def show_error_window(text: str):
    show_popup_window(
        title="Error", text=text, image_paths=(ERROR_DARK_PATH, ERROR_LIGHT_PATH)
    )
