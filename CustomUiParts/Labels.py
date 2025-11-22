from customtkinter import CTkLabel

from Project.settings import FONT_MENU, FONT_ADDITIONAL


class StandardLabel(CTkLabel):
    """Стандартный лейбл с текстом (текст выделить нельзя)"""

    def __init__(self, master, text, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            text=text,
            font=FONT_MENU
        )


class DescriptionLabel(CTkLabel):
    """Лейбл для текста, который обычно несет дополнительную информацию с пояснениями"""

    def __init__(self, master, text, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            text=text,
            text_color="grey",
            font=FONT_ADDITIONAL,
            wraplength=350,
            height=10
        )
