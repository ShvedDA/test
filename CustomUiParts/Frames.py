import queue

from customtkinter import CTkFrame

from Project.Tables.CommonCustomTable import CommonCustomTable
from .Buttons import MenuButton
from .Labels import StandardLabel
from .MessageBoxes.SpecialMessageBoxes import SuccessMessageBox


class StandardFrame(CTkFrame):
    """Стандартный основной фрейм в программе"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # всплывающее окно
        self.current_window = None  # сюда передаем всплывающее окно
        self.message_text = None  # сюда передаем сообщение
        # Создаем очередь для контролирования закрытия окна
        self.message_queue = queue.Queue()

    def get_last_grid_row(self):
        """Получаем индекс последней строки Grid Layot"""
        last_row = -1
        # Проверяем все виджеты
        for child in self.winfo_children():
            # Получаем информацию о grid layot
            grid_info = child.grid_info()
            if grid_info:
                row = grid_info["row"]
                last_row = max(last_row, row)
        return last_row + 1 if last_row != -1 else 0

    def add_to_last_row(self, widget, **grid_kwargs):
        """Добавляем виджет как последний элемент в Grid"""
        last_row = self.get_last_grid_row()
        widget.grid(row=last_row, **grid_kwargs)
        return last_row

    def check_queue(self):
        """Check the queue for messages from the background thread."""
        try:
            message = self.message_queue.get_nowait()
            if message == "close":
                # Безопасно закрываем открытое окно
                self.current_window.destroy()
                SuccessMessageBox(self.master, self.message_text)
                return
        except queue.Empty:
            pass
        self.after(100, self.check_queue)


class MenuFrame(StandardFrame):
    """Шаблон окна кнопок меню"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.configure(
            fg_color="transparent",
            bg_color="transparent"
        )
        self.button_list = []
        self.pack_propagate(False)

    def create_button(self, master, name, text, command):
        if not master:
            master = self
        return MenuButton(master, name, text, command)

    def add_button(self, master, name, text, command):
        """Метод, чтобы добавить одну кнопку"""
        button = self.create_button(master, name, text, command)
        button.pack(
            fill="x",
            pady=(5, 5)
        )
        self.button_list.append(button)

    def add_buttons(self, buttons):
        """
        Метод, чтобы добавить несколько кнопок из коллекции,
        состощяй из экземпляторв датакласса MenuButtonData
        """
        for index, (name, text, command) in enumerate(buttons):
            menu_button = self.create_button(self, name, text, command)
            self.button_list.append(menu_button)
            menu_button.pack(
                fill="x"
            )
            if index == 0:
                menu_button.pack(
                    pady=(0, 5)
                )
            else:
                menu_button.pack(
                    pady=(5, 5)
                )

    def return_button(self, input_name):
        """Возвращаем кнопку по её имени"""
        for btn in self.button_list:
            if btn.name == input_name:
                return btn
        return None


class TableWithHeaderFrame(CTkFrame):
    """Фрейм с таблицей и её названием"""

    def __init__(self, master, header_text, columns, **kwargs):
        super().__init__(master, **kwargs)
        self.default_text = header_text
        self.configure(
            fg_color="transparent",
            bg_color="transparent"
        )
        # конфигурация
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, minsize=20)
        self.grid_rowconfigure(1, weight=1)
        # заголовок
        degault_pad = (5, 5)
        self.bootLabel = StandardLabel(self, text=header_text)
        self.bootLabel.grid(row=0, column=0, pady=degault_pad, sticky='nsew')
        # таблица
        self.bootTableFrame = CommonCustomTable(self, columns)
        self.bootTableFrame.grid(row=1, column=0, pady=degault_pad, sticky='nsew')

    def update_data(self, data):
        """
        Обновить данные в таблице (сначала все стираем, потом добавляем данные в коллекции).
        Данные должны быть представлены списком кортежей.
        Пример: [(1, "John Doe", "Admin", True), (2, "Jane Doe", "User", False)]
        """
        self.bootTableFrame.remove_data()
        self.bootTableFrame.insert_data(data)

    def clean_data(self):
        self.bootTableFrame.remove_data()

    def insert_data(self, data):
        """
        Вставляем данные в таблицу.
        Данные должны быть представлены списком кортежей.
        Пример: [(1, "John Doe", "Admin", True), (2, "Jane Doe", "User", False)]
        """
        if isinstance(data[0], dict):
            self.bootTableFrame.insert_data_from_dictcollection(data)
        else:
            self.bootTableFrame.insert_data(data)

    def return_selected_item(self):
        """Возвращаем выбранный элемент"""
        return self.bootTableFrame.selected_item

    def get_table_headers(self):
        return self.bootTableFrame.treeview['columns']

    def update_header(self, new_text=None):
        """Меняем заголовок таблицы для отображения"""
        if new_text:
            self.bootLabel.configure(text=f"{self.default_text} ({new_text})")
        else:
            self.bootLabel.configure(text=self.default_text)

    def return_all_data(self):
        """Возвращаем все значения"""
        return self.bootTableFrame.return_all_data()
