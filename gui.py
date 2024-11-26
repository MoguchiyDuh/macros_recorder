import customtkinter


# Function to show a custom message box
def show_messagebox(title, message):
    # Create a new Toplevel window (popup)
    messagebox = customtkinter.CTkToplevel()
    messagebox.title(title)
    messagebox.geometry("300x150")

    # Add a message label
    label = customtkinter.CTkLabel(
        messagebox, text=message, wraplength=250, font=("Arial", 14)
    )
    label.pack(pady=20)

    # Add a button to close the message box
    close_button = customtkinter.CTkButton(
        messagebox, text="OK", command=messagebox.destroy
    )
    close_button.pack(pady=10)

    # Ensure the message box is modal
    messagebox.transient()
    messagebox.grab_set()
    messagebox.wait_window()


# Example usage
def on_button_click():
    show_messagebox("CustomTkinter MessageBox", "This is a custom message box!")


# Main application
app = customtkinter.CTk()
app.geometry("400x200")
app.title("CustomTkinter Example")

button = customtkinter.CTkButton(app, text="Show MessageBox", command=on_button_click)
button.pack(pady=50)

app.mainloop()
