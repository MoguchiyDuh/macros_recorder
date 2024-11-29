import customtkinter as ctk
from popup_window import PopupWindow


def open_popup():
    # Create a popup window
    popup = PopupWindow(root)
    popup.grab_set()  # Ensures the popup window is modal


# Initialize the main application
root = ctk.CTk()
root.title("Main Application")
root.geometry("400x300")

# Button to open popup
open_popup_button = ctk.CTkButton(root, text="Open Popup", command=open_popup)
open_popup_button.pack(pady=20)


root.mainloop()
