import tkinter
from customtkinter import CTkToplevel, CTkLabel, CTkFrame

from Project.settings import IMAGES_DIR
from Project.utils import resource_path
from .Frames import StandardFrame
from .TextFrames import TextBlockedFrame
from .Buttons import CustomUserButtons, OkButton


class NotificationWindow(CTkToplevel):
    """
    Стандартное окно уведомления
    При появлении блокирует взаимодействие пользователя с другими окнами
    Если было скрыто, то становится видимым.
    """

    def __init__(self, error_text, pad_x, pad_y, window_w, window_h, state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.withdraw()
        self.geometry(f"{window_w}x{window_h}+{pad_x}+{pad_y}")
        self.resizable(False, False)
        self.label = CTkLabel(self, text=error_text)
        self.okButton = OkButton(self, self.ok_click)
        self.label.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
        self.okButton.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)
        self.grab_set()  # блокируем взаимодействие пользователя с другими окнами

        # в зависимости от статуса меняем название окна и иконку
        if state:
            self.title("Ошибка!")
            error_image = resource_path(IMAGES_DIR / "error.ico")
            if error_image.is_file():
                self.after(200, lambda: self.iconbitmap(error_image))
            else:
                print(f"icon {error_image} is not found")
        else:
            succes_image = resource_path(IMAGES_DIR / "success.ico")
            self.title("Успех!")
            if succes_image.is_file():
                self.after(200, lambda: self.iconbitmap(succes_image))
            else:
                print(f"icon {succes_image} is not found")

        self.deiconify()  # показываем окно, если скрыто

    # команда для кнопки ОК, закрывает окно
    def ok_click(self):
        self.destroy()


class VerticalTextContainer(StandardFrame):
    """
    Фрейм в состав, которого входят TextFrame, расположенные вертикально
    """

    def __init__(self, master, labels_texts, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color='transparent')

        # self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.text_frames = []
        self.set_labels(labels_texts)

    def set_labels(self, labels_texts):
        """
        Добавляем TextFrame, на основе коллекции кортежей: (описание, изменяемый текст)
        """
        label_list = list(labels_texts)
        for i in range(len(label_list)):
            self.grid_rowconfigure(i, weight=1)

        for index, (description, text) in enumerate(label_list):
            new_text = TextBlockedFrame(self, description, text)
            self.text_frames.append(new_text)
            new_text.grid(
                row=index,
                column=0,
                sticky="nsw",  # Прижимаем к левому краю
                padx=5,
            )


class HorizontalButtonContainer(CTkFrame):
    """
    Фрейм в состав, которого входят кнопки расположенные горизонтально
    """

    def __init__(self, master, buttons_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(fg_color='transparent')
        self.rowconfigure(0, weight=1)
        self.buttons = []
        self.add_buttons(buttons_data)

    def add_buttons(self, buttons_data):
        """
        Информация по кнопкам должны быть представлена в коллекции кортежей в виде:
        [(name, text, command) ...]
        """
        # добавляем кнопки
        for index, (name, text, state, command) in enumerate(buttons_data):
            button = CustomUserButtons(
                master=self,
                name=name,
                text=text,
                state=state,
                command=command
            )
            self.buttons.append(button)
            self.grid_columnconfigure(index, weight=1)
            if index == 0:
                pad = (10, 5)
            else:
                pad = (5, 5)
            button.grid(row=0, column=index, padx=pad)
        # настраиваем отступ для последней кнопки
        last_button = self.buttons[-1]
        last_index = len(self.buttons) - 1
        last_button.grid_forget()
        last_button.grid(row=0, column=last_index, padx=(5, 10))

    def find_button(self, button_name):
        """Ищем кнопку по имени"""
        for button in self.buttons:
            if button.name == button_name:
                return button

    def add_command_to_button(self, button_name, new_command):
        """Добавляем новую команду"""
        button = self.find_button(button_name)
        button.configure(command=new_command)

    def turn_on_button(self, button_name):
        """Включаем кнопку по её имени"""
        button = self.find_button(button_name)
        button.configure(state="normal")

    def turn_off_button(self, button_name):
        """Выключаем кнопку по её имени"""
        button = self.find_button(button_name)
        button.configure(state="disabled")
