from customtkinter import CTkComboBox

from Project.settings import FONT_MENU


class StandardComboBox(CTkComboBox):
    """
    Стандартный комбобокс со списком текстовых значений.
    Без возможности вписать своё значение.
    По-умолчанию первое значение из списка
    """

    def __init__(self, master, list_values, default_value, **kwargs):
        super().__init__(master, **kwargs)
        self.default_value = default_value
        self.configure(
            values=list_values,
            font=FONT_MENU
        )
        self.set(self.default_value)
