from tkinter import BooleanVar
from customtkinter import CTkFrame
from abc import ABC, abstractmethod

from Project.CustomUiParts.ComboBoxes import StandardComboBox
from Project.CustomUiParts.Labels import StandardLabel
from Project.CustomUiParts.Switches import StandardSwitch
from Project.CustomUiParts.TextParts import StandardText, EditableText


class FrameWithUserData(ABC):
    """Абстрактный класс для имплементации методом для текстовых фреймов с пользовательскими значениями"""

    @abstractmethod
    def get_data(self):
        """Получаем данные"""
        pass

    @abstractmethod
    def set_data(self, *args):
        """Вставляем данные"""
        pass

    @abstractmethod
    def clean_data(self):
        """Приводим к значению по-умолчанию"""
        pass


class EntryFrameWithText(CTkFrame, FrameWithUserData):
    """Стандартный фрейм с данными и описанием"""

    def __init__(self, master, description_text, new_object, main_text="", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color='transparent')

        # Настройки сетки
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  # Растягиваем текстовое поле

        # Описание (левый край)
        self.description = StandardLabel(self, text=f"{description_text}: ")
        self.description.grid(row=0, column=0, sticky="w")

        # Текст (растягиваем на оставшееся место)
        self.text_result = new_object(self, new_text=main_text)
        self.text_result.grid(
            row=0,
            column=1,
            sticky="ew",  # Растягиваем по горизонтали
            padx=5
        )

    def get_data(self):
        """Получаем данные из текстового поля"""
        return self.text_result.get_full_text()

    def set_data(self, value):
        """Обновляем текст без pack_forget()"""
        self.text_result.set_text(value)

    def clean_data(self):
        """Невозможно почистить, так как неизвестно что будет задано в объекте"""
        pass

    def show_result(self, value):
        """Меняем данные из текстового поля"""
        if not value:
            self.text_result.pack_forget()
        else:
            self.text_result.pack(side='right')


class TextBlockedFrame(EntryFrameWithText):
    """Стандартный фрейм с текстом StandardText, текст заблокирован,
    меняется только через внутренний метод set_data"""

    def __init__(self, master, description_text, main_text="", **kwargs):
        super().__init__(master, description_text, StandardText, main_text, **kwargs)

    def clean_data(self):
        """Зачищаем полностью текст"""
        self.text_result.delete_all_data()


class EditableTextFrame(EntryFrameWithText):
    """Стандартный фрейм с изменяемым текстом"""

    def __init__(self, master, description_text, main_text="", validate_rule=None, **kwargs):
        super().__init__(master, description_text, EditableText, main_text, **kwargs)
        if validate_rule:
            # Добавляем валидацию к Entry
            self.add_validate_rule(validate_rule)

    def clean_data(self):
        """Зачищаем полностью текст"""
        self.text_result.delete(0, 'end')

    def change_placeholder_text(self, new_text):
        """Обновляем текст"""
        self.text_result.configure(placeholder_text=new_text)

    def change_width(self, value):
        """Меняем ширину инпута пользователя"""
        self.text_result.configure(width=value)

    def delete_last(self):
        """Удаляем последний символ"""
        self.text_result.delete_last_symbol()

    def split_text(self):
        """Чистим поле ввода от лишних пробелов, убираем двойные пробелы"""
        current_text = self.get_data().split()
        self.clean_data()
        self.set_data(current_text)

    def add_validate_rule(self, validate_rule):
        """Добавляем валидацию к Entry"""
        self.text_result.configure(
            validate="key",
            validatecommand=validate_rule
        )

    def delete_validate_rule(self):
        """Убираем валидацию пользовательского ввода в Entry"""
        self.text_result.configure(
            validate=None,
            validatecommand=()
        )


class SwitchFrame(CTkFrame, FrameWithUserData):
    """Фрейм с описанием и свитчом"""

    def __init__(self, master, description_text, main_text, default=True, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color='transparent')

        # Настройки сетки
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  # Растягиваем текстовое поле

        # Описание (левый край)
        self.description = StandardLabel(self, text=f"{description_text}: ")
        self.description.grid(row=0, column=0, sticky="w")

        # Свитч
        self.status_var = BooleanVar(value=default)
        self.status_switch = StandardSwitch(self, text=main_text, boolean_variable=self.status_var)
        self.status_switch.grid(
            row=0,
            column=1,
            sticky="ew",  # Растягиваем по горизонтали
            padx=5
        )

    def get_data(self):
        """Получаем положение свитча"""
        return self.status_switch.get()

    def set_data(self, state=True):
        """
        Переводим свитч в положение в зависимости от state.
        True - включаем, False - выключаем
        """
        if state:
            self.status_switch.select()
        else:
            self.status_switch.deselect()

    def clean_data(self):
        """Выставляем на ON"""
        self.status_switch.select()

    def block_switch(self, state=False):
        if state:
            self.status_switch.configure(state="disabled")
        else:
            self.status_switch.configure(state="normal")


class ComboBoxFrame(CTkFrame, FrameWithUserData):
    """Фрейм с комбобоксом"""

    def __init__(self, master, description_text, list_values, default, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color='transparent')

        # Настройки сетки
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  # Растягиваем текстовое поле

        # Описание (левый край)
        self.description = StandardLabel(self, text=f"{description_text}: ")
        self.description.grid(row=0, column=0, sticky="w")

        # Комбобокс с выбором
        self.comboBox = StandardComboBox(self, list_values, default)
        self.comboBox.grid(
            row=0,
            column=1,
            sticky="ew",  # Растягиваем по горизонтали
            padx=5
        )

    def get_data(self):
        """Возвращаем выбранный пункт в комбобоксе"""
        return self.comboBox.get()

    def set_data(self, value):
        """Выставляем значение по индексу"""
        self.comboBox.set(value)

    def clean_data(self):
        """Выставляем по-умолачнию"""
        self.comboBox.set(self.comboBox.default_value)
