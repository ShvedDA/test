from pathlib import Path
from tkinter import Label

from Project.CustomUiParts.Buttons import StandardButton
from Project.CustomUiParts.Entries import StandardEntry, PasswordEntry
from Project.CustomUiParts.Frames import StandardFrame
from Project.CustomUiParts.ImageLabels import ImageLabel
from Project.CustomUiParts.Labels import StandardLabel

from Project.Services.ValidationsRules import validate_login_name, validate_entries
from Project.settings import BLOCK_COLOR, ALLOW_COLOR


class LoginFrame(StandardFrame):
    """
    Основной фрейм окна авторизации пользователя
    Кнопка без команды.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i + 1, minsize=35)
        self.grid_rowconfigure(7, weight=1)

        self.loginLabel = StandardLabel(self, "Пожалуйста, войдите в Ваш рабочий профиль!")
        # создаем поле ввода логина, запрещаем в поле ввод пробелов
        no_spaces = (self.register(validate_login_name), "%S")
        self.loginEntry = StandardEntry(self, "Введите логин", validate='key',
                                        validatecommand=no_spaces)
        self.passwordEntry = PasswordEntry(self, "Введите пароль", validate='key', validatecommand=no_spaces)
        self.login_phrase = "Пожалуйста, введите учетные данные"
        self.loadingImage = ImageLabel(self)
        self.loginStatus = None
        self.setup_ui_parts()  # располагаем объекты во фрейме
        self.loginButton = StandardButton(self, button_text="Войти", width=80)
        self.disable_button()
        self.status_row = self.get_last_grid_row()
        self.first_login_attemp()
        # добавляем кнопку последним фреймом
        self.loginButton.grid(row=self.status_row + 1, column=0, sticky='NS')

        # биндим проверку, чтобы кнопку можно было нажать только при заполненных полях
        for entry in (self.loginEntry, self.passwordEntry):
            entry.bind("<KeyRelease>",
                       lambda e: validate_entries(e, self.loginButton, self.loginEntry, self.passwordEntry))

    def first_login_attemp(self):
        """Исходный вид окна"""
        self.loginStatus = StandardLabel(self, self.login_phrase, text_color="grey")
        self.grid_status_row(self.loginStatus)

    def grid_status_row(self, ui_object):
        """Ставим объект на место статуса"""
        pad = 16
        if isinstance(ui_object, Label):
            pad = 0
        ui_object.grid(row=self.status_row, column=0, pady=pad, sticky='NS')

    def setup_ui_parts(self):
        """Растановка элементов"""
        elements = (
            self.loginLabel,
            self.loginEntry,
            self.passwordEntry,
        )
        for index, element in enumerate(elements):
            element.grid(row=index + 1, column=0, pady=5, sticky='NS')

    def change_login_status(self, any_object=None, state=True):
        """
        Меняем статус во фрейме
        Если передаем картинку, то обязательно указать путь к картинке в виде Path
        """
        if isinstance(any_object, str):
            color = BLOCK_COLOR
            if state:
                color = ALLOW_COLOR
            self.loginStatus.configure(text=any_object, text_color=color)
        elif isinstance(any_object, Path):
            # отключаем свитч
            if hasattr(self.master, "menuFrame"):
                self.master.menuFrame.switch.switch.configure(state='disabled')

            self.loginStatus.grid_remove()
            self.grid_status_row(self.loadingImage)
            self.loadingImage.load(any_object)
        elif not any_object:
            self.loginStatus.configure(
                text=self.login_phrase,
                text_color='grey')

    def remove_gif(self):
        """Убираем изображение и возвращаем обратно надпись статуса"""
        if self.loadingImage:
            self.loadingImage.unload()
            self.loadingImage.grid_remove()

        # отключаем свитч
        if hasattr(self.master, "menuFrame"):
            self.master.menuFrame.switch.switch.configure(state='normal')

        self.grid_rowconfigure(0, weight=1)  # Ensure row expands
        self.grid_columnconfigure(0, weight=1)
        self.update_idletasks()

    def read_userinput(self):
        """Возвращаем инпут пользователя кортежом: (логин, пароль)"""
        return self.loginEntry.get(), self.passwordEntry.get()

    def add_command_to_frame(self, user_command):
        self.loginButton.configure(
            command=user_command
        )

    def disable_button(self):
        self.loginButton.configure(state='disabled')

    def enable_button(self):
        self.loginButton.configure(state='normal')

    def complete_cleanup(self):
        """Полностью зачищаем"""
        # отключаем свитч
        if hasattr(self.master, "menuFrame"):
            self.master.menuFrame.switch.switch.configure(state='normal')

        self.remove_gif()
        self.loginStatus.grid()
        self.enable_button()
        self.update_idletasks()

    def clean_user_input(self):
        """Зачищаем ввод пользователья"""
        self.loginEntry.delete(0, 'end')
        self.passwordEntry.delete(0, 'end')
