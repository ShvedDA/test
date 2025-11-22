from tkinter import BooleanVar

from PIL import Image
from customtkinter import CTkSwitch, CTkImage, CTkFrame, CTkLabel, get_appearance_mode, set_appearance_mode

from Project.settings import FONT_MENU, IMAGES_DIR
from Project.utils import resource_path


class StandardSwitch(CTkSwitch):
    """Стандартный свитч в приложении"""

    def __init__(self, master, text, boolean_variable: BooleanVar, **kwargs):
        super().__init__(master, onvalue=True, offvalue=False, **kwargs)
        self.configure(
            text=text,
            font=FONT_MENU,
            variable=boolean_variable
        )


class ThemeSwitch(CTkFrame):
    """Свитч переключения темы приложения"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Загружаем иконки
        self.light_image = CTkImage(Image.open(resource_path(IMAGES_DIR / "light_theme.png")))
        self.dark_image = CTkImage(Image.open(resource_path(IMAGES_DIR / "dark_theme.png")))

        # Сам свитч
        self.switch = CTkSwitch(self, text="", switch_width=36, width=36, command=self.toggle_theme)
        self.switch.pack(side="left", padx=(5, 0))

        # Добавляем иконку
        self.theme_icon = CTkLabel(self, text="", image=self.light_image)
        self.theme_icon.pack(side="left", padx=(0, 5))

        # Выставляем текущую тему
        self.current_theme = get_appearance_mode()
        if self.current_theme == "Dark":
            self.switch.select()
            self.set_dark_theme()

    def set_dark_theme(self):
        set_appearance_mode("Dark")

        # если есть конфигурация стиля таблиц
        root = self.winfo_toplevel()
        if hasattr(root, "configure_treeview_style"):
            root.configure_treeview_style("Dark")

        self.theme_icon.configure(image=self.dark_image)

    def set_light_theme(self):
        set_appearance_mode("Light")

        # если есть конфигурация стиля таблиц
        root = self.winfo_toplevel()
        if hasattr(root, "configure_treeview_style"):
            root.configure_treeview_style("Light")

        self.theme_icon.configure(image=self.light_image)

    def toggle_theme(self):
        """Команда смены темы для свитча"""
        if self.switch.get() == 1:  # Switch is ON
            self.set_dark_theme()
        else:  # Switch is OFF
            self.set_light_theme()
