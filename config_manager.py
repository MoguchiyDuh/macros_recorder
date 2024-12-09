import json
import os

from colorama import Fore


CONFIG_TEMPLATE = {"recording_hotkey": "ctrl+alt+]", "theme": "dark", "langauge": "eng"}


def load_config():
    try:
        with open("./config.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR]{Fore.RESET}: Config not found!")
        with open("./config.json", "w") as file:
            json.dump(CONFIG_TEMPLATE, file, indent=4)
        config = CONFIG_TEMPLATE
    except json.JSONDecodeError as e:
        print(
            f"{Fore.RED}[ERROR]{Fore.RESET}: Config is corrupted! Using default config! {e}"
        )
        config = CONFIG_TEMPLATE
    return config


def update_config(data: dict):
    with open("./config.json", "w") as file:
        json.dump(data, file, indent=4)


def load_macro_list() -> dict[dict]:
    macros_list = {}
    for root, dirs, files in os.walk("./macros"):
        for file in files:
            macro_name, extension = os.path.splitext(file)
            if extension == ".json":
                with open(os.path.join(root, file), "r") as f:
                    try:
                        macro = json.load(f)
                    except json.JSONDecodeError:
                        print(
                            f"{Fore.RED}[ERROR]{Fore.RESET}: Macro {macro_name} is corrupted! Skipping..."
                        )
                        continue

                    macros_list[macro_name] = macro
    return macros_list


def add_macro(macro_name: str, macro: dict):
    with open(os.path.join("./macros", macro_name + ".json"), "w") as file:
        json.dump(macro, file, indent=4)


def edit_macro(macro_name: str, macro: dict):
    with open(os.path.join("./macros", macro_name + ".json"), "w") as file:
        json.dump(macro, file, indent=4)


def delete_macro(macro_name: str):
    macro_path = os.path.join("./macros", macro_name + ".json")
    if os.path.exists(macro_path):
        os.remove(macro_path)
    else:
        print(f"{Fore.RED}[ERROR]{Fore.RESET}: Macro {macro_name} not found!")


def get_langs() -> list:
    lang_list = []
    for root, dirs, files in os.walk("./assets/localization"):
        for file in files:
            lang, extension = os.path.splitext(file)
            if extension == ".json":
                lang_list.append(lang)

    return lang_list


def load_localization(lang: str) -> dict:
    localization = None
    for root, dirs, files in os.walk("./assets/localization"):
        for file in files:
            lang_name, extension = os.path.splitext(file)
            if lang == lang_name:
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
