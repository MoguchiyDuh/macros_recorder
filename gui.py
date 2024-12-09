import os
import sys
from time import sleep
import customtkinter as ctk
import tkinter as tk
from keyboard import add_hotkey, remove_hotkey
from PIL import Image

from macros_controller import MacroController
from config_manager import get_langs, load_config, update_config, load_localization
from popup_window import PopupWindow


class App(ctk.CTk):
    def __init__(self, window_size: tuple[int], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ===============VARIABLES===============
        self.CONFIG = load_config()
        self.LOCALIZATION = load_localization(self.CONFIG["lang"])
        self.THEME_PATH = "./assets/themes"
        self.change_theme(theme=self.CONFIG["theme"], init=True)

        self.CTK_COLOR = ctk.ThemeManager.theme["CTk"]["fg_color"]
        self.FONTBOLD = ctk.CTkFont(**ctk.ThemeManager.theme["MacrosFontBold"])
        self.selected_macro = None
        self.IS_RECORDING = False

        self.mc = MacroController()

        # ===============APP SETUP===============
        self.title("Macros Recorder")
        self.iconbitmap(ctk.ThemeManager.theme["Icons"]["MacrosIcon"])
        self.geometry(f"{window_size[0]}x{window_size[1]}")
        self.resizable(False, False)
        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)

        for macro_name, info in self.mc.macros_list.items():
            if info["is_active"]:
                self.mc.enable_macro(macro_name=macro_name)

        # ===============ICONS===============
        ICON_SIZE = (35, 35)
        self.settings_icon = ctk.CTkImage(
            light_image=Image.open(
                ctk.ThemeManager.theme["Icons"]["MacrosSettingsIcon"]
            ),
            dark_image=Image.open(
                ctk.ThemeManager.theme["Icons"]["MacrosSettingsIcon"]
            ),
            size=ICON_SIZE,
        )
        self.back_icon = ctk.CTkImage(
            light_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosBackIcon"]),
            dark_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosBackIcon"]),
            size=ICON_SIZE,
        )
        self.add_icon = ctk.CTkImage(
            light_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosAddIcon"]),
            dark_image=Image.open(ctk.ThemeManager.theme["Icons"]["MacrosAddIcon"]),
            size=ICON_SIZE,
        )
        self.discord_icon = ctk.CTkImage(
            light_image=Image.open(ctk.ThemeManager.theme["Icons"]["DiscordLogoIcon"]),
            dark_image=Image.open(ctk.ThemeManager.theme["Icons"]["DiscordLogoIcon"]),
            size=ICON_SIZE,
        )

        # ===============MAIN PAGE WIDGETS===============
        self.main_page = ctk.CTkFrame(self, fg_color=self.CTK_COLOR)
        self.main_page.grid_rowconfigure(index=0, weight=1)
        self.main_page.grid_rowconfigure(index=1, weight=0)
        self.main_page.grid_columnconfigure(index=1, weight=1)

        # ----------Frames----------
        MACROS_LIST_WIDTH = 125
        self.scrollable_macros_list_frame = ctk.CTkScrollableFrame(
            self.main_page,
            width=MACROS_LIST_WIDTH,
        )
        self.scrollable_macros_list_frame.grid_columnconfigure(index=0, weight=1)
        self.scrollable_macros_list_frame.grid_rowconfigure(index=0, weight=1)

        INFO_FRAME_WIDTH = 325
        INVIS_FRAME_HEIGHT = 30
        INSIDE_INFO_FRAME_SIZE = (400, 45)
        self.info_frame = ctk.CTkFrame(self.main_page, width=INFO_FRAME_WIDTH)
        self.info_frame.grid_columnconfigure(index=0, weight=1)

        self.macro_name_frame = ctk.CTkFrame(
            self.info_frame,
            width=INSIDE_INFO_FRAME_SIZE[0],
            height=INSIDE_INFO_FRAME_SIZE[1],
        )

        self.macro_name_frame.grid_columnconfigure(index=0, weight=1)
        self.macro_name_frame.grid_columnconfigure(index=1, weight=1)
        self.macro_name_frame.grid_columnconfigure(index=2, weight=1)
        self.set_hotkey_frame = ctk.CTkFrame(
            self.info_frame,
            width=INSIDE_INFO_FRAME_SIZE[0],
            height=INSIDE_INFO_FRAME_SIZE[1],
        )

        self.set_hotkey_frame.grid_columnconfigure(index=0, weight=1)
        self.set_hotkey_frame.grid_columnconfigure(index=1, weight=1)
        self.set_hotkey_frame.grid_columnconfigure(index=2, weight=1)

        self.loop_frame = ctk.CTkFrame(
            self.info_frame,
            width=INSIDE_INFO_FRAME_SIZE[0],
            height=INSIDE_INFO_FRAME_SIZE[1],
        )

        self.loop_frame.grid_columnconfigure(index=0, weight=1)
        self.loop_frame.grid_columnconfigure(index=1, weight=1)

        self.invis_frame = ctk.CTkFrame(
            self.main_page,
            width=MACROS_LIST_WIDTH,
            height=INVIS_FRAME_HEIGHT,
            fg_color=self.CTK_COLOR,
        )  # for settings and add buttons
        self.invis_frame.grid_rowconfigure(index=0, weight=1)
        self.invis_frame.grid_columnconfigure(index=0, weight=1)
        self.invis_frame.grid_columnconfigure(index=1, weight=1)

        self.invis_frame2 = ctk.CTkFrame(
            self.main_page,
            width=INFO_FRAME_WIDTH,
            height=INVIS_FRAME_HEIGHT,
            fg_color=self.CTK_COLOR,
        )  # for enable/disable, delete buttons
        self.invis_frame2.grid_rowconfigure(index=0, weight=1)
        self.invis_frame2.grid_columnconfigure(index=0, weight=1)
        self.invis_frame2.grid_columnconfigure(index=1, weight=1)

        # ----------Macro Info----------
        BUTTON_SIZE = (100, 35)
        ENTRY_WIDTH = 100
        FRAME_COLOR = ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
        self.macro_name_label = ctk.CTkLabel(
            self.macro_name_frame, text=self.LOCALIZATION["macro_name_label"]
        )
        self.macro_name_button = ctk.CTkButton(
            self.macro_name_frame,
            bg_color=FRAME_COLOR,
            fg_color=FRAME_COLOR,
            hover_color=FRAME_COLOR,
            text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"],
            font=self.FONTBOLD,
            command=self.macro_name_button_callback,
        )

        SET_BUTTON_WIDTH = 50
        self.rename_entry = ctk.CTkEntry(self.macro_name_frame, width=ENTRY_WIDTH)
        self.rename_button = ctk.CTkButton(
            self.macro_name_frame,
            width=SET_BUTTON_WIDTH,
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["set_button"],
            font=self.FONTBOLD,
            command=lambda: self.rename_button_callback(self.rename_entry.get()),
        )

        self.set_hotkey_label = ctk.CTkLabel(
            self.set_hotkey_frame,
            text=self.LOCALIZATION["hotkey_label"],
        )
        self.set_hotkey_entry = ctk.CTkEntry(self.set_hotkey_frame, width=ENTRY_WIDTH)
        self.set_hotkey_button = ctk.CTkButton(
            self.set_hotkey_frame,
            width=SET_BUTTON_WIDTH,
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["set_button"],
            font=self.FONTBOLD,
            command=lambda: self.set_hotkey_button_callback(
                self.set_hotkey_entry.get()
            ),
        )

        self.loop_switch_label = ctk.CTkLabel(
            self.loop_frame, text=self.LOCALIZATION["loop_switch_label"]
        )
        self.loop_switch_var = tk.Variable(value=False)
        self.loop_switch = ctk.CTkSwitch(
            self.loop_switch_label,
            text="",
            variable=self.loop_switch_var,
        )

        self.edit_macro_button = ctk.CTkButton(
            self.info_frame,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["edit_macro_button"],
            font=self.FONTBOLD,
            command=self.edit_button_callback,
        )
        # ----------Record New Macro----------
        # macro name from Macro Info
        self.new_macro_name_entry = ctk.CTkEntry(
            self.macro_name_frame, width=ENTRY_WIDTH
        )

        # set_hotkey_label and set_hotkey_entry from Macro Info

        self.recording_status_label = ctk.CTkLabel(
            self.info_frame, text="", font=self.FONTBOLD
        )

        # ----------Invis Frame 1 (bottom left) Widgets----------
        self.settings_button = ctk.CTkButton(
            self.invis_frame,
            width=ICON_SIZE[0],
            height=ICON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
            text="",
            image=self.settings_icon,
            command=self.show_settings_page,
        )

        self.add_macro_button = ctk.CTkButton(
            self.invis_frame,
            width=ICON_SIZE[0],
            height=ICON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
            text="",
            image=self.add_icon,
            command=self.show_new_macro,
        )

        # ----------Invis Frame 2 (bottom right) Widgets----------
        self.toggle_status_var = tk.StringVar(
            value=self.LOCALIZATION["status_enable_button"]
        )
        self.toggle_macro_status_button = ctk.CTkButton(
            self.invis_frame2,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosToggleActiveButton"]["enable"],
            font=self.FONTBOLD,
            command=lambda: self.change_status_callback(
                self.toggle_status_var.get()
                == self.LOCALIZATION["status_enable_button"]
            ),
            textvariable=self.toggle_status_var,
        )

        self.delete_macro_button = ctk.CTkButton(
            self.invis_frame2,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["delete_button"],
            font=self.FONTBOLD,
            command=self.delete_button_callback,
        )

        self.save_new_macro_button = ctk.CTkButton(
            self.invis_frame2,
            width=BUTTON_SIZE[0],
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["save_button"],
            font=self.FONTBOLD,
            command=lambda: self.save_button_callback(
                macro_name=self.new_macro_name_entry.get(),
                hotkey=self.set_hotkey_entry.get(),
            ),
        )

        # ===============SETTINGS PAGE WIDGETS===============
        self.settings_page = ctk.CTkFrame(self, fg_color=self.CTK_COLOR)
        self.settings_page.grid_columnconfigure(index=0, weight=1)

        # ----------Back Button----------
        self.back_button = ctk.CTkButton(
            self.settings_page,
            width=ICON_SIZE[0],
            height=ICON_SIZE[1],
            **ctk.ThemeManager.theme["MacrosButtonWithIcon"],
            text="",
            image=self.back_icon,
            command=self.show_main_page,
        )

        # ----------Frames----------
        SETTINGS_FRAME_SIZE = (400, 45)

        self.theme_frame = ctk.CTkFrame(
            self.settings_page,
            width=SETTINGS_FRAME_SIZE[0],
            height=SETTINGS_FRAME_SIZE[1],
        )
        self.theme_frame.grid_rowconfigure(index=0, weight=1)
        self.theme_frame.grid_columnconfigure(index=0, weight=1)
        self.theme_frame.grid_columnconfigure(index=1, weight=1)

        self.lang_frame = ctk.CTkFrame(
            self.settings_page,
            width=SETTINGS_FRAME_SIZE[0],
            height=SETTINGS_FRAME_SIZE[1],
        )
        self.lang_frame.grid_rowconfigure(index=0, weight=1)
        self.lang_frame.grid_columnconfigure(index=0, weight=1)
        self.lang_frame.grid_columnconfigure(index=1, weight=1)

        self.set_recording_hotkey_frame = ctk.CTkFrame(
            self.settings_page,
            width=SETTINGS_FRAME_SIZE[0],
            height=SETTINGS_FRAME_SIZE[1],
        )
        self.set_recording_hotkey_frame.grid_rowconfigure(index=0, weight=1)
        self.set_recording_hotkey_frame.grid_columnconfigure(index=0, weight=1)
        self.set_recording_hotkey_frame.grid_columnconfigure(index=1, weight=1)
        self.set_recording_hotkey_frame.grid_columnconfigure(index=2, weight=1)

        # ----------Select Theme Widgets----------
        self.select_theme_label = ctk.CTkLabel(
            self.theme_frame,
            text=self.LOCALIZATION["select_theme_label"],
            font=self.FONTBOLD,
        )
        self.themes_option_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=self.available_themes(),
            command=self.change_theme,
        )
        self.themes_option_menu.set(self.CONFIG["theme"])

        # ----------Select Lang Widgets----------
        self.select_lang_label = ctk.CTkLabel(
            self.lang_frame,
            text=self.LOCALIZATION["select_lang_label"],
            font=self.FONTBOLD,
        )
        self.langs_option_menu = ctk.CTkOptionMenu(
            self.lang_frame,
            values=get_langs(),
            command=self.change_lang,
        )
        self.langs_option_menu.set(self.CONFIG["lang"])

        # ----------Set Recording Hotkey Widgets----------
        self.set_recording_hotkey_label = ctk.CTkLabel(
            self.set_recording_hotkey_frame,
            text=self.LOCALIZATION["hotkey_label"],
            font=self.FONTBOLD,
        )
        self.set_recording_hotkey_entry = ctk.CTkEntry(
            self.set_recording_hotkey_frame, width=ENTRY_WIDTH
        )
        self.set_recording_hotkey_entry.delete(0, ctk.END)
        self.set_recording_hotkey_entry.insert(0, self.CONFIG["recording_hotkey"])
        self.set_recording_hotkey_button = ctk.CTkButton(
            self.set_recording_hotkey_frame,
            width=SET_BUTTON_WIDTH,
            height=BUTTON_SIZE[1],
            text=self.LOCALIZATION["set_button"],
            font=self.FONTBOLD,
            command=lambda: self.set_recording_hotkey_callback(
                self.set_recording_hotkey_entry.get()
            ),
        )

    # ===============FUNCTIONS===============
    def change_theme(self, theme: str | None = "dark", init: bool | None = False):
        ctk.set_default_color_theme(os.path.join(self.THEME_PATH, theme + ".json"))
        if init:
            return
        self.CONFIG["theme"] = theme
        update_config(self.CONFIG)
        # I'm lazy to update all widgets manualy, so.. just restart the app
        os.execv(sys.executable, ["python"] + sys.argv)

    def change_lang(self, lang: str):
        self.CONFIG["lang"] = lang
        self.LOCALIZATION = load_localization(lang=lang)
        update_config(self.CONFIG)

        self.delete_macro_button.configure(text=self.LOCALIZATION["delete_button"])
        self.select_theme_label.configure(text=self.LOCALIZATION["select_theme_label"])
        self.select_lang_label.configure(text=self.LOCALIZATION["select_lang_label"])

        self.macro_name_label.configure(text=self.LOCALIZATION["macro_name_label"])
        self.rename_button.configure(text=self.LOCALIZATION["set_button"])
        self.set_hotkey_label.configure(text=self.LOCALIZATION["hotkey_label"])
        self.set_hotkey_button.configure(text=self.LOCALIZATION["set_button"])
        self.loop_switch_label.configure(text=self.LOCALIZATION["loop_switch_label"])
        self.edit_macro_button.configure(text=self.LOCALIZATION["edit_macro_button"])
        self.save_new_macro_button.configure(text=self.LOCALIZATION["save_button"])
        self.set_recording_hotkey_label.configure(
            text=self.LOCALIZATION["hotkey_label"]
        )
        self.set_recording_hotkey_button.configure(text=self.LOCALIZATION["set_button"])

    def available_themes(self):
        themes_list = []
        for root, dirs, files in os.walk(self.THEME_PATH):
            for file in files:
                theme_name, extension = os.path.splitext(file)
                if extension == ".json":
                    themes_list.append(theme_name)
        return themes_list

    # ===============PAGE MANAGEMENT===============
    def clear_frame(self, frame: ctk.CTkFrame | None = None):
        if frame is not None:
            for widget in frame.winfo_children():
                widget.grid_forget()
        else:
            for widget in self.winfo_children():
                widget.grid_forget()
        try:
            remove_hotkey(hotkey_or_callback=self.CONFIG["recording_hotkey"])
        except KeyError:
            pass

    def show_main_page(self):
        self.clear_frame()
        self.main_page.grid(row=0, column=0, sticky="nsew")
        self.scrollable_macros_list_frame.grid(
            row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="nsew"
        )
        self.info_frame.grid(row=0, column=1, padx=(5, 10), pady=(10, 5), sticky="nsew")
        self.info_frame.grid_propagate(False)
        self.invis_frame.grid(
            row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew"
        )
        self.invis_frame2.grid(
            row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nsew"
        )
        self.settings_button.grid(row=0, column=0)
        self.add_macro_button.grid(row=0, column=1)

        self.show_macro_list()

    def clear_macro_info_frame(self):
        self.clear_frame(frame=self.info_frame)
        self.clear_frame(frame=self.invis_frame2)
        self.clear_frame(frame=self.macro_name_frame)
        self.clear_frame(frame=self.set_hotkey_frame)
        self.clear_frame(frame=self.loop_frame)

    def show_macro_info(self):
        self.clear_macro_info_frame()
        self.macro_name_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nwe")
        self.set_hotkey_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nwe")
        self.loop_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nwe")

        self.macro_name_label.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="w")
        self.macro_name_button.grid(row=0, column=1, sticky="nsew")
        self.macro_name_button.configure(text=self.selected_macro["name"])

        self.set_hotkey_label.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="w")
        self.set_hotkey_entry.grid(row=0, column=1, padx=10, pady=5)
        self.set_hotkey_entry.delete(0, ctk.END)
        self.set_hotkey_entry.insert(0, self.selected_macro["hotkey"])
        self.set_hotkey_button.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="e")

        self.loop_switch_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.loop_switch.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.edit_macro_button.grid(row=3, column=0, pady=10)

        self.toggle_macro_status_button.grid(row=0, column=0)
        self.delete_macro_button.grid(row=0, column=1)

    def show_new_macro(self):
        self.clear_macro_info_frame()
        self.selected_macro = None
        self.show_macro_list()
        self.new_macro_name_entry.delete(0, ctk.END)
        self.new_macro_name_entry.insert(0, "Untitled")

        self.macro_name_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nwe")
        self.set_hotkey_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nwe")

        self.macro_name_label.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="w")
        self.new_macro_name_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)

        self.set_hotkey_label.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="w")
        self.set_hotkey_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)
        self.set_hotkey_entry.delete(0, ctk.END)
        self.set_hotkey_entry.insert(0, "ctrl+alt+1")

        self.recording_status_label.configure(text=self.LOCALIZATION["not_recording"])
        self.recording_status_label.grid(row=3, column=0, pady=(10, 0))

        self.save_new_macro_button.grid(row=0, column=0, columnspan=2)

        add_hotkey(
            hotkey=self.CONFIG["recording_hotkey"],
            callback=self.toggle_recording_callback,
        )

    def show_macro_list(self):
        self.clear_frame(frame=self.scrollable_macros_list_frame)
        self.clear_macro_info_frame()
        self.selected_macro = None

        self.macros_list_buttons = []
        self.mc.update_macro_list()
        for macro_name in self.mc.macros_list.keys():
            macro_select_button = ctk.CTkButton(
                self.scrollable_macros_list_frame,
                **ctk.ThemeManager.theme["MacrosListButton"]["normal"],
                text=macro_name,
                command=lambda name=macro_name: self.show_selected_macro(name),
            )
            self.macros_list_buttons.append(macro_select_button)

        for index, macro_select_button in enumerate(self.macros_list_buttons):
            macro_select_button.configure(
                **ctk.ThemeManager.theme["MacrosListButton"]["normal"]
            )
            macro_select_button.grid(
                row=index, column=0, padx=5, pady=(5, 0), sticky="nwe"
            )

    def show_selected_macro(self, selected_macro_name: str):
        for macro_select_button in self.macros_list_buttons:
            macro_select_button: ctk.CTkButton
            if selected_macro_name == macro_select_button.cget("text"):
                macro_select_button.configure(
                    **ctk.ThemeManager.theme["MacrosListButton"]["selected"]
                )
                macro_name = macro_select_button.cget("text")
                self.selected_macro = self.mc.macros_list[macro_name]
                self.selected_macro["name"] = macro_name
                self.show_macro_info()
            else:
                macro_select_button.configure(
                    **ctk.ThemeManager.theme["MacrosListButton"]["normal"]
                )

        self.change_status_callback(
            status=self.selected_macro["is_active"], only_visual=True
        )

    def show_settings_page(self):
        self.clear_frame()
        self.settings_page.grid(row=0, column=0, sticky="nsew")
        self.back_button.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")

        self.theme_frame.grid(row=1, column=0, padx=80, pady=(30, 0), sticky="nwe")
        self.lang_frame.grid(row=2, column=0, padx=80, pady=(10, 0), sticky="nwe")
        self.set_recording_hotkey_frame.grid(
            row=3, column=0, padx=80, pady=(10, 0), sticky="nwe"
        )

        self.select_theme_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.themes_option_menu.grid(row=0, column=1, padx=(5, 10), pady=5)

        self.select_lang_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.langs_option_menu.grid(row=0, column=1, padx=(5, 10), pady=5)

        self.set_recording_hotkey_label.grid(
            row=0, column=0, padx=(10, 0), pady=5, sticky="w"
        )
        self.set_recording_hotkey_entry.grid(row=0, column=1, padx=10, pady=5)
        self.set_recording_hotkey_button.grid(row=0, column=2, padx=(0, 10), pady=5)

    # ===============CALLBACKS===============
    # ----------Main Page----------
    def change_status_callback(self, status: bool, only_visual: bool | None = None):
        if status:  # if True, change from Enable to Disable state
            self.toggle_macro_status_button.configure(
                **ctk.ThemeManager.theme["MacrosToggleActiveButton"]["disable"]
            )
            self.toggle_status_var.set(value=self.LOCALIZATION["status_disable_button"])
            if not only_visual:
                self.mc.enable_macro(self.selected_macro["name"])
        else:
            self.toggle_macro_status_button.configure(
                **ctk.ThemeManager.theme["MacrosToggleActiveButton"]["enable"]
            )
            self.toggle_status_var.set(value=self.LOCALIZATION["status_enable_button"])
            if self.selected_macro["is_active"] and not only_visual:
                self.mc.disable_macro(self.selected_macro["name"])

    def edit_button_callback(self):
        os.startfile(
            os.path.join(os.getcwd(), "macros", self.selected_macro["name"] + ".json")
        )

    def macro_name_button_callback(self):
        self.macro_name_button.grid_forget()
        self.rename_entry.grid(row=0, column=1, padx=(10, 5), pady=5)
        self.rename_entry.insert(0, self.selected_macro["name"])
        self.rename_button.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")

    def rename_button_callback(self, new_macro_name: str):
        if new_macro_name == "":
            PopupWindow(self).show_error_window(text="Empty macro name")
            return

        self.change_status_callback(status=False)
        output = self.mc.edit_macro(
            macro_name=self.selected_macro["name"], new_macro_name=new_macro_name
        )
        if output == "ERROR":
            PopupWindow(self).show_error_window(
                text="File with this name already exists"
            )
            return
        self.focus()
        self.rename_entry.delete(0, ctk.END)
        self.rename_button.grid_forget()
        self.rename_entry.grid_forget()
        self.show_macro_list()
        self.show_selected_macro(new_macro_name)

    def set_hotkey_button_callback(self, hotkey: str):
        active = self.selected_macro["is_active"]
        if active:
            self.mc.disable_macro(macro_name=self.selected_macro["name"])

        self.selected_macro["hotkey"] = hotkey
        self.mc.edit_macro(macro_name=self.selected_macro["name"], hotkey=hotkey)

        if active:
            self.mc.enable_macro(macro_name=self.selected_macro["name"])
        self.focus()
        PopupWindow(self).show_info_window(text=f"Hotkey set to: {hotkey}")

    def delete_button_callback(self):
        self.mc.disable_macro(macro_name=self.selected_macro["name"])
        self.mc.delete_macro(macro_name=self.selected_macro["name"])
        self.show_macro_list()

    def save_button_callback(self, macro_name: str | None, hotkey: str | None):
        pw = PopupWindow(self)
        if macro_name is None:
            pw.show_error_window(text="Empty macro name")
            return
        elif hotkey is None:
            pw.show_error_window(text="Hotkey not set")
            return
        elif self.mc.recorded_macro_actions == []:
            pw.show_error_window(text="No actions recorded")
            return
        else:
            self.mc.add_macro(
                macro_name=macro_name,
                actions=self.mc.recorded_macro_actions,
                hotkey=hotkey,
                is_active=False,
            )
            self.selected_macro = {
                "name": macro_name,
                "actions": self.mc.recorded_macro_actions,
                "hotkey": hotkey,
                "is_active": False,
            }
            pw.show_info_window(text=f"Macro {macro_name} saved")
            self.show_macro_list()

    def toggle_recording_callback(self):
        self.IS_RECORDING = not self.IS_RECORDING
        if self.IS_RECORDING:
            sleep(0.5)
            self.recording_status_label.configure(text=self.LOCALIZATION["recording"])
            self.mc.start_recording()
        else:
            self.recording_status_label.configure(text=self.LOCALIZATION["recorded"])
            self.mc.stop_recording()

    # ----------Settings Page----------
    def set_recording_hotkey_callback(self, hotkey: str):
        if hotkey == "":
            PopupWindow(self).show_error_window(text="Recording Hotkey not set")
            return

        self.focus()
        self.CONFIG["recording_hotkey"] = hotkey
        update_config(self.CONFIG)

        PopupWindow(self).show_info_window(
            text=f"Recording Hotkey changed to: \n{hotkey}"
        )
