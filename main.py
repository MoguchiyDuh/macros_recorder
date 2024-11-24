import keyboard


def print_hello():
    print("Hello")


keyboard.add_hotkey("[", print_hello)
keyboard.wait("esc")
