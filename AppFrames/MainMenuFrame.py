from pathlib import Path

from Project.CustomUiParts.Frames import MenuFrame, StandardFrame
from Project.CustomUiParts.ImageLabels import ImageLabel
from Project.CustomUiParts.Switches import ThemeSwitch
from Project.DataClasses.MenuButtonsData import buttons_data, get_prepared_collection, authButton


class MainMenu(StandardFrame):
    """
    Стандартный фрейм окна меню с кнопками, комманды кнопок не заданы.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, minsize=25)
        self.grid_rowconfigure(1, weight=1)
        # свитч для переключения темы
        self.switch = ThemeSwitch(self)
        self.switch.grid(row=0, column=0, sticky="NS")

        self.menu_buttons = MenuFrame(self)
        self.add_buttons()
        self.menu_buttons.grid(row=1, column=0, padx=10, sticky="NSEW")  # располагаем кнопки по-середине
        # добавление гифки прогрузки
        self.loadingImage = ImageLabel(self)
        self.gif_row = self.add_to_last_row(self.loadingImage, padx=10, pady=10, sticky="NS")
        # добавляем нижнию кнопку входа
        self.add_button_to_bottom(authButton.get_common_data())

        self.remove_gif()

    def add_buttons(self):
        self.menu_buttons.add_buttons(get_prepared_collection(buttons_data))  # добавляем кнопки без команд

    def add_button_to_bottom(self, button_data):
        """Добавляем кнопку внизу"""
        new_button = self.menu_buttons.create_button(self, *button_data)
        self.menu_buttons.button_list.append(new_button)
        self.add_to_last_row(new_button, padx=10, pady=10, sticky="NSEW")

    def get_button_list(self):
        return self.menu_buttons.button_list

    def get_button_names(self):
        return tuple(map(lambda x: x.name, self.get_button_list()))

    def get_button(self, search_name):
        return self.menu_buttons.return_button(search_name)

    def add_command_to_button(self, button_name, new_command: callable):
        button = self.get_button(button_name)
        button.configure(command=new_command)

    def add_command_to_all_button(self, command: callable, collection: dict):
        for button in self.get_button_list():
            button.configure(command=lambda btn=button: command(btn.name, collection))

    def start_loadgif(self, any_object):
        """Начало анимации гиф"""
        if isinstance(any_object, Path):
            self.switch.switch.configure(state='disabled')
            self.loadingImage.unload()
            self.loadingImage.grid(row=self.gif_row, column=0, padx=10, pady=10, sticky="NS")
            self.loadingImage.load(any_object)
            self.update_idletasks()

    def remove_gif(self):
        """Убираем изображение и возвращаем обратно надпись статуса"""
        self.switch.switch.configure(state='normal')
        self.loadingImage.unload()
        self.loadingImage.grid_forget()
