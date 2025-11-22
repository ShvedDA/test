from typing import Callable

from PIL import Image
from customtkinter import CTkButton, CTkImage

from Project.settings import RED_BG_COLOR, FONT_ELEMENTS, FONT_MENU, IMAGES_DIR
from Project.utils import resource_path


class StandardButton(CTkButton):
    """Стандартная кнопка в проекте"""

    def __init__(self, master, button_text="", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            font=FONT_ELEMENTS,
            fg_color=RED_BG_COLOR,
            text=button_text
        )

    def turn_on(self):
        self.configure(state="normal")

    def turn_off(self):
        self.configure(state='disabled')


class OkButton(StandardButton):
    """Стандартная кнопка ОК"""

    # конструктор принимает окно, метод/функцию без аргументов, возвращающая None
    def __init__(self, master, command: Callable[[], None], **kwargs):
        super().__init__(master, button_text='OK', **kwargs)
        self.configure(
            height=27,
            width=75,
            command=command,
        )


class MenuButton(StandardButton):
    """Стандартные кнопки в меню"""

    def __init__(self, master, name, text, command=None, **kwargs):
        super().__init__(master, text, **kwargs)
        self.name = name
        self.configure(
            anchor="center",
            height=50,
            font=FONT_MENU,
            command=command,
        )


class CustomUserButtons(StandardButton):
    """Кнопки, которые использются для действий в основном окне"""

    def __init__(self, master, name, text, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.name = name
        self.configure(
            anchor="center",
            width=130,
            height=30,
            text=text,
            font=FONT_MENU,
            command=command,
        )


class KeyButton(StandardButton):
    """Маленькая кнопка с ключиком на картинке"""

    def __init__(self, master, **kwargs):
        # картинка с ключиком
        btn_light = Image.open(resource_path(IMAGES_DIR / "key_light.png"))
        btn_dark = Image.open(resource_path(IMAGES_DIR / "key_dark.png"))

        ctk_image = CTkImage(light_image=btn_light, dark_image=btn_dark, size=(24, 24))
        # передаем картинку в конструктор напрямую
        super().__init__(master, text="", image=ctk_image, width=40, **kwargs)
        self.name = 'keyButton'  # имя для поиска
