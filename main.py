from gui import App

WINDOW_SIZE = (500, 400)

if __name__ == "__main__":
    app = App(WINDOW_SIZE)
    app.show_main_page()
    app.show_macro_list()
    app.mainloop()
