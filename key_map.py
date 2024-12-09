import win32con

KEY_MAP = {
    # Mouse keys
    "LMB": win32con.VK_LBUTTON,
    "RMB": win32con.VK_RBUTTON,
    "MMB": win32con.VK_MBUTTON,
    "MB4": win32con.VK_XBUTTON1,
    "MB5": win32con.VK_XBUTTON2,
    # Spec keys
    "WIN": win32con.VK_LWIN,
    "Backspace": win32con.VK_BACK,
    "Tab": win32con.VK_TAB,
    "Enter": win32con.VK_RETURN,
    "Shift": win32con.VK_SHIFT,
    "Ctrl": win32con.VK_CONTROL,
    "Alt": win32con.VK_MENU,
    "Caps Lock": win32con.VK_CAPITAL,
    "Esc": win32con.VK_ESCAPE,
    "Space": win32con.VK_SPACE,
    "Left Arrow": win32con.VK_LEFT,
    "Up Arrow": win32con.VK_UP,
    "Right Arrow": win32con.VK_RIGHT,
    "Down Arrow": win32con.VK_DOWN,
    "Insert": win32con.VK_INSERT,
    "Delete": win32con.VK_DELETE,
    "Home": win32con.VK_HOME,
    "End": win32con.VK_END,
    "Page Up": win32con.VK_PRIOR,
    "Page Down": win32con.VK_NEXT,
    "F1": win32con.VK_F1,
    "F2": win32con.VK_F2,
    "F3": win32con.VK_F3,
    "F4": win32con.VK_F4,
    "F5": win32con.VK_F5,
    "F6": win32con.VK_F6,
    "F7": win32con.VK_F7,
    "F8": win32con.VK_F8,
    "F9": win32con.VK_F9,
    "F10": win32con.VK_F10,
    "F11": win32con.VK_F11,
    "F12": win32con.VK_F12,
    # Special characters and symbols
    "`": 0xC0,  # Backtick (`) key
    "-": 0xBD,  # Dash (-) key
    "=": 0xBB,  # Equals (=) key
    "[": 0xDB,  # Left square bracket ([)
    "]": 0xDD,  # Right square bracket (])
    "\\": 0xDC,  # Backslash (\)
    ";": 0xBA,  # Semicolon (;)
    "'": 0xDE,  # Apostrophe (')
    ",": 0xBC,  # Comma (,)
    ".": 0xBE,  # Period (.)
    "/": 0xBF,  # Forward slash (/)
}

for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
    KEY_MAP[char] = ord(char)

MOUSE_MAP = {
    # Mouse buttons
    "LMB": {
        "down": win32con.MOUSEEVENTF_LEFTDOWN,
        "up": win32con.MOUSEEVENTF_LEFTUP,
        "flag": 0,
    },
    "RMB": {
        "down": win32con.MOUSEEVENTF_RIGHTDOWN,
        "up": win32con.MOUSEEVENTF_RIGHTUP,
        "flag": 0,
    },
    "MMB": {
        "down": win32con.MOUSEEVENTF_MIDDLEDOWN,
        "up": win32con.MOUSEEVENTF_MIDDLEUP,
    },
    "MB4": {
        "down": win32con.MOUSEEVENTF_XDOWN,
        "up": win32con.MOUSEEVENTF_XUP,
        "flag": win32con.VK_XBUTTON1,
    },
    "MB5": {
        "down": win32con.MOUSEEVENTF_XDOWN,
        "up": win32con.MOUSEEVENTF_XUP,
        "flag": win32con.VK_XBUTTON2,
    },
}
