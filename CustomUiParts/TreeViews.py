from tkinter import ttk
from customtkinter import CTkFrame

from Project.utils import int_from_str


class StandardTreeview(CTkFrame):
    """Стандартный вид таблицы"""

    def __init__(self, master, columns, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color="transparent",
            bg_color="transparent"
        )

        # Создаем общий фрейм для таблицы
        self.tree_frame = CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        # Создаем виджет таблицы
        headers = tuple(map(lambda x: x[0], columns))
        self.treeview = ttk.Treeview(self.tree_frame, columns=headers, show="headings", height=21)
        # Добавляем столбцы в таблицу
        self.add_columns(columns)
        # прописываем логику и биндинг выбора строка выбора
        self.selected_item: tuple = tuple()
        self.treeview.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        """
        Получаем данные из таблицы в виде кортежа
        event оставляем, так как передается вместе с событием. Без него работать не будет.
        """
        selected_items = self.get_selected_data()  # Получаем ВСЕ выделенные элементы

        if not selected_items:  # Если ничего не выделено
            self.selected_item = tuple()
            return
        selected_item = selected_items[0]  # Берём первый выделенный элемент
        self.selected_item = self.search_row(selected_item)
        return True

    def set_objects(self):
        self.treeview.pack(fill="both", expand=True)

    def add_columns(self, columns):
        """
        Добавить столбцы в таблицу. Данные должны быть представлены коллекцией кортежей, вида:
        (name, header_name, width, anchor)
        """
        for name, header_name, width, anchor in columns:
            self.treeview.column(name, width=width, anchor=anchor)
            self.treeview.heading(name, text=header_name)

    def insert_data(self, data):
        """
        Добавить данные в таблицу. Данные должны быть представлены списком кортежей.
        Пример: [(1, "John Doe", "Admin", True), (2, "Jane Doe", "User", False)]
        """
        for row in data:
            self.treeview.insert("", "end", values=row)

    def remove_data(self):
        """Удаляем все строки в таблице"""
        self.treeview.delete(*self.treeview.get_children())

    def update_data(self, data):
        """Обновляем строки в таблице"""
        self.remove_data()
        self.insert_data(data)

    def return_all_data(self):
        """Возвращаем все данные в таблице в виде кортежа"""
        items_values = []
        for item in self.treeview.get_children():
            items_values.append(self.treeview.item(item, 'values'))
        return items_values

    def get_selected_data(self):
        """Передаем выбор пользователя из таблицы"""
        return self.treeview.selection()

    def search_row(self, selected_item):
        """Ищем строку по выбору пользователя в таблице"""
        return self.treeview.item(selected_item, 'values')

    def insert_data_from_dictcollection(self, dict_values: list[dict]):
        """
        Вставляем данные в таблицу на основе полученного словаря с названиями столбцов
        Полезно при получении данных по API
        """

        def get_tuple_from_dict(dct):
            return tuple(map(lambda x: dct[x], self.treeview['columns']))

        data = map(
            get_tuple_from_dict,
            dict_values
        )
        self.insert_data(data)

    def get_all_items(self, parent=''):
        """Получаем все строки из таблицы"""
        items = []
        for child in self.treeview.get_children(parent):
            items.append(child)
        return items

    def scroll_to_last_item(self, searched_text=None):
        """Скролим таблицу до конца"""

        all_items = self.get_all_items()

        if not all_items:
            return

        last_item = all_items[-1]  # Get the last item in the list

        # Expand all parent nodes of the last item
        current_item = last_item
        while True:
            parent = self.treeview.parent(current_item)
            if not parent:  # Stop when reaching the root
                break
            self.treeview.item(parent, open=True)  # Expand the parent
            current_item = parent  # Move up to the parent

        # Scroll to the last item
        self.treeview.see(last_item)


class ScrollableVerticalTreeview(StandardTreeview):
    """
    Таблица с вертикальным скроллбаром,
    горизонтально таблица будет всегда вписана в родительский фрейм
    """

    def __init__(self, master, columns, **kwargs):
        total_width = master.winfo_reqwidth()
        widths = tuple(map(lambda x: x[2], columns))
        total_weight = sum(widths)
        col_widths = (int(total_width * (w / total_weight)) for w in widths)
        updated_columns = tuple(map(
            lambda old, new: (old[0], old[1], new, old[3]),
            columns, col_widths
        ))

        super().__init__(master, updated_columns, **kwargs)

        # Добавляем вертикальный и горизонтальный скроллбар
        self.v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.v_scrollbar.set)

    def set_objects(self):
        self.v_scrollbar.pack(side="right", fill="y")
        super().set_objects()


class ScrollableTreeview(StandardTreeview):
    """Таблица с вертикальным и горизонтальными скроллбарами"""

    def __init__(self, master, columns, **kwargs):
        super().__init__(master, columns, **kwargs)

        # Добавляем вертикальный и горизонтальный скроллбар
        self.v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.treeview.yview)
        self.h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.treeview.xview)

        self.treeview.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

    def set_objects(self):
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        super().set_objects()


class SortedTreeView(StandardTreeview):
    """Таблица с возможностью сортировки по клику на заголовок"""

    def __init__(self, master, columns, **kwargs):
        super().__init__(master, columns, **kwargs)
        # Атрибуты для хранения информации по сортировке таблицы
        self.sorted_column = None
        self.sort_order = True  # True - убывание, False - возрастание

        # Привязываем сортировку к кликам на заголовки
        for idx, (column_id, *_) in enumerate(columns):
            # Настраиваем команду для заголовка
            self.treeview.heading(
                column_id,
                command=lambda cn=idx: self.sort_column(column=cn)
            )

    def sort_column(self, column=None):
        """
        Сортирует данные по указанной колонке.
        Меняет порядок сортировки при повторном клике на тот же заголовок.
        """
        # Собираем данные из всех строк
        data = [(self.treeview.item(item)["values"], item)[0]
                for item in self.treeview.get_children()]

        # Определяем направление сортировки
        if column == self.sorted_column:
            self.sort_order = not self.sort_order
        else:
            self.sort_order = True

        # Выполняем сортировку
        all_digits = all(map(lambda x: True if type(x[column]) == int else x[column].isdigit(), data))

        if all_digits:
            data.sort(key=lambda x: int_from_str(x[column]), reverse=self.sort_order)
        else:
            data.sort(key=lambda x: str(x[column]), reverse=self.sort_order)

        # Перезаполняем таблицу
        self.treeview.delete(*self.treeview.get_children())
        self.insert_data(data)

        # Обновляем информацию о сортировке
        self.sorted_column = column
