from abc import ABC
from PIL import Image

from customtkinter import CTkToplevel, CTkImage, CTkFrame, CTk

from Project.CustomUiParts.Buttons import OkButton, StandardButton
from Project.CustomUiParts.Labels import StandardLabel
from Project.settings import IMAGES_DIR, ALLOW_COLOR
from Project.utils import resource_path, relative_center


class MessageBox(CTkToplevel, ABC):
    """Абстрактный класс для мессаджбоксов"""

    def __init__(self, master: (CTk, CTkFrame), height, width, title, description_text, **kwargs):
        super().__init__(master)
        self.grab_set()
        self._setup_appearance(title)
        self.resizable(False, False)
        self._setup_window(master, height, width)

        # колонка для картинки
        self.grid_columnconfigure(0, minsize=60)
        self.grid_columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # текст
        self.text = StandardLabel(self, text=description_text, justify='center')
        self.text.grid(row=0, column=1)

        # гиф или картинка
        self.icon = None

    def _setup_window(self, master, height, width):
        x, y = relative_center(
            master.winfo_x(),
            master.winfo_y(),
            master.winfo_width(),
            master.winfo_height(),
            width,
            height
        )
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_appearance(self, new_title):
        self.title(new_title)
        # Иконка добавляется через async так, как есть баг во фреймворке, описан гите:
        # https://github.com/TomSchimansky/CustomTkinter/issues/1163
        self.after(200, lambda: self.iconbitmap(resource_path(IMAGES_DIR / "iconRus.ico")))

    def setup_icon(self, icon_name: str, dark_icon_name: str = None):
        """Устанавливаем иконку окна"""
        total_size = (60, 60)

        # выбираем иконки для тем
        icon = Image.open(resource_path(IMAGES_DIR / icon_name))
        dark_icon = icon

        # если задана иконка для темной темы
        if dark_icon_name:
            dark_icon = Image.open(resource_path(IMAGES_DIR / dark_icon_name))

        # ставим иконку
        ctk_image = CTkImage(light_image=icon, dark_image=dark_icon, size=total_size)
        self.icon = StandardLabel(self, text="", image=ctk_image)
        self.icon.grid(row=0, column=0, padx=(20, 10), sticky='nsew')


class OkMessageBox(MessageBox, ABC):
    def __init__(self, master: (CTk, CTkFrame), height, width, title, description_text, **kwargs):
        super().__init__(master, height, width, title, description_text, **kwargs)
        self.grid_rowconfigure(1, minsize=50)
        print(description_text)
        self.ok_button = OkButton(self, command=self._click_ok)
        self.ok_button.grid(row=1, column=0, columnspan=2, pady=10, sticky='ns')

    def _click_ok(self):
        self.destroy()


class YesOrNoMessageBox(MessageBox, ABC):
    def __init__(self, master: (CTk, CTkFrame), height, width, title, description_text, **kwargs):
        super().__init__(master, height, width, title, description_text, **kwargs)
        self.grid_rowconfigure(1, minsize=50)
        self.user_response = None  # Храним ответ пользователя (True/False)

        # Фрейм с кнопками
        self.buttons = CTkFrame(self, fg_color='transparent')
        self.buttons.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.buttons.grid_rowconfigure(0, weight=1)
        self.buttons.grid_columnconfigure(0, weight=1)
        self.buttons.grid_columnconfigure(1, weight=1)

        # Выставляем кнопки
        self.yes_button = StandardButton(self.buttons, 'Да', command=self._click_yes)
        self.yes_button.configure(fg_color=ALLOW_COLOR)
        self.yes_button.grid(row=0, column=0, padx=(40, 10))
        self.no_nutton = StandardButton(self.buttons, 'Нет', command=self._click_no)
        self.no_nutton.grid(row=0, column=1, padx=(10, 40))

    def _click_yes(self):
        self.user_response = True
        self.destroy()

    def _click_no(self):
        self.user_response = False
        self.destroy()

    def wait_response(self) -> bool:
        """Соыбтие при закрытии окна"""
        self.wait_window()  # Blocks until the window is destroyed
        return self.user_response


class TextWithDescriptionInMessageBox(MessageBox, ABC):
    """
    Класс содержит рассширенный текст,
    во втором лейбле можно сделать текст другого формата
    """

    def __init__(self, master: (CTk, CTkFrame), height, width, title, description_text, additional_text, **kwargs):
        super().__init__(master, height, width, title, description_text, **kwargs)

        # текстовый фрейм
        self.text = CTkFrame(self, fg_color='transparent')
        self.text.grid_rowconfigure(0, weight=1)
        self.text.grid_rowconfigure(1, weight=1)
        self.text.grid_columnconfigure(0, weight=1)
        self.text.grid(row=0, column=1)

        # основной текст
        self.main_text = StandardLabel(self.text, text=description_text, justify='center')
        self.main_text.grid(row=0, column=0)

        # дополнительный текст
        self.additional_text = StandardLabel(self.text, text=additional_text, justify='left')
        self.additional_text.grid(row=1, column=0)
