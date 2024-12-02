import json
import os

from colorama import Fore


CONFIG_TEMPLATE = {"recording_hotkey": "ctrl+alt+]", "theme": "main", "langauge": "eng"}


def load_config():
    try:
        with open("./config.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Config not found!")
        with open("./config.json", "w") as file:
            json.dump(CONFIG_TEMPLATE, file)
        config = CONFIG_TEMPLATE
    except json.JSONDecodeError as e:
        print("Config is corrupted! Using default config! {e}")
        config = CONFIG_TEMPLATE
    return config


def update_config(data: dict):
    with open("./config.json", "w") as file:
        json.dump(data, file)


def load_macro_list() -> list[dict]:
    with open("./macros.json", "r") as file:
        macros_list = json.load(file)
    return macros_list


def update_macro_list(data: list):
    with open("./macros.json", "w") as file:
        json.dump(data, file)


def load_localization(lang: str) -> dict:
    localization = None
    for root, dirs, files in os.walk("./assets/localization"):
        for file in files:
            if lang.lower()[:3] in file[:3]:
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    localization = json.load(f)
                    break
    if localization is None:
        print(
            f"{Fore.RED}[ERROR]{Fore.RESET}: Localization not found! Using default localization..."
        )
        with open("./assets/localizations/eng.json", "r") as f:
            localization = json.load(f)

    return localization
