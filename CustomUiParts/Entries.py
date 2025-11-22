from customtkinter import CTkEntry

from Project.settings import FONT_ELEMENTS


class StandardEntry(CTkEntry):
    """Стандартное поле ввода"""

    def __init__(self, master, placeholder_text, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            placeholder_text=placeholder_text,
            width=270,
            justify="left",
            corner_radius=20,
            font=FONT_ELEMENTS
        )


class PasswordEntry(StandardEntry):
    """Стандартное поле ввода для пароля"""

    def __init__(self, master, placeholder_text, **kwargs):
        super().__init__(master, placeholder_text, **kwargs)
        self.configure(show="*")
