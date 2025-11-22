from sqlalchemy import False_

from Project.AppFrames.AdditionalWindows.AddNewFirmwareWindow import AddNewFirmwareWindow
from Project.CustomUiParts.Frames import TableWithHeaderFrame, StandardFrame
from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox, SuccessMessageBox, ConfirmMessageBox
from Project.CustomUiParts.Windows import HorizontalButtonContainer
from Project.DataClasses.ColumnsData import allDevicesFirmwareColumns, get_prepared_collection
from Project.DataClasses.UserInterfaceButtons import allFirmwareButtons
from Project.settings import FIRMWARE_TYPES
from Project.task_manager import task_manager
from Project.utils import str_to_bool


class FirmwareFrameRelease(StandardFrame):
    """Окно для работы с прошивками"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if hasattr(master, "api_manager"):
            self.api_manager = master.api_manager
        self.grid_propagate(False)
        # конфигурируем фрейм
        self.grid_columnconfigure(0, weight=1)
        # делим фрейм условно на 3 части
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.grid_rowconfigure(3, minsize=20)

        # Коллекции/Итераторы для таблиц
        self.table_columns = tuple(map(
            lambda x: x.get_common_columndata(),
            allDevicesFirmwareColumns
        ))

        # таблица с прошивками загрузчика
        self.bootTableFrame = TableWithHeaderFrame(
            self,
            header_text="Прошивка загрузчика",
            columns=self.table_columns
        )
        self.bootTableFrame.grid(row=0, column=0, pady=(5, 0), sticky="nsew")

        # таблица с прошивками PST-контроллера
        self.pstTableFrame = TableWithHeaderFrame(
            self,
            header_text="Прошивка PST-контроллера (стадия \"Релиз\")",
            columns=self.table_columns
        )
        self.pstTableFrame.grid(row=1, column=0, sticky="nsew")

        # таблица с прошивками позиционера
        self.posTableFrame = TableWithHeaderFrame(
            self,
            header_text="Прошивка позиционера (стадия \"Релиз\")",
            columns=self.table_columns
        )
        self.posTableFrame.grid(row=2, column=0, sticky="nsew")

        # панель кнопок, названия кнопок совпадает с кнопками с фрейма Пользовательский по причине идентичности кнопок
        self.command_buttons = HorizontalButtonContainer(self, get_prepared_collection(allFirmwareButtons))
        self.command_buttons.add_command_to_button("reloadButton", self.reload_command)
        self.command_buttons.add_command_to_button("addUsersButton", self.add_new_firmware)
        self.command_buttons.add_command_to_button("editUsersButton", self.edit_firmware)

        self.command_buttons.grid(row=3, column=0, pady=(0, 5), sticky='w')

        # Название таблицы и её ссылка
        self.dict_firmwares = {
            "firmware_boot": self.bootTableFrame,
            "firmware_pst": self.pstTableFrame,
            "firmware_pos": self.posTableFrame
        }

        # последняя выбранная таблица
        self.clicked_treeview = None
        self.bootTableFrame.bootTableFrame.treeview.bind("<<TreeviewSelect>>",
                                                         self.bootTableFrame.bootTableFrame.on_select)
        self.bootTableFrame.bootTableFrame.treeview.bind('<Button-1>', self.on_treeview_click, add='+')
        self.pstTableFrame.bootTableFrame.treeview.bind('<Button-1>', self.on_treeview_click, add='+')
        self.posTableFrame.bootTableFrame.treeview.bind('<Button-1>', self.on_treeview_click, add='+')

    def async_reload_data(self):
        """Обновляем данные об оборудовании в таблице и записываем значения таблицы в self.table_data"""
        if not hasattr(self, "api_manager"):
            return

        if hasattr(self.master, "async_update_table"):
            for table in self.dict_firmwares:
                self.master.async_update_table(
                    data_func=lambda tbl=table: self.api_manager.get_all_firmware_files(tbl, False),
                    headers=self.dict_firmwares[table].get_table_headers(),
                    update_func=self.dict_firmwares[table].update_data,
                    callback = self.dict_firmwares[table].bootTableFrame.scroll_to_last_item)

    def get_all_data(self):
        """Получаем словарь со значениями всей таблицы"""
        firmware_data = {}
        dict_keys = tuple(map(lambda x: x[0], self.table_columns))
        for firmware in self.dict_firmwares:
            table_data = self.dict_firmwares[firmware].bootTableFrame.return_all_data()
            dict_data = list(map(
                lambda x: {key: value for key, value in zip(dict_keys, x)},
                table_data
            ))
            firmware_data[firmware] = dict_data

        return firmware_data

    def reload_command(self):
        """Команда обновления таблицы"""
        self.async_reload_data()

    def add_new_firmware(self):
        """Команда добавления новой прошивки"""
        self.current_window = AddNewFirmwareWindow(self, self.get_all_data(), False)
        self.check_queue()

    def edit_firmware(self):
        """Команда редактирования новой прошивки"""
        firmware_data = self.clicked_treeview.selected_item

        clicked_table = self.clicked_treeview.master
        for type_firmware, frame in self.dict_firmwares.items():
            if frame == clicked_table:
                clicked_table = type_firmware

        ru_clicked_table = FIRMWARE_TYPES[clicked_table]

        # окно для подтверждения удаления
        confirmation_window = ConfirmMessageBox(
            self.master,
            f"Версия {firmware_data[1]} станет активной.\nВсе остальные прошивки типа\n'{ru_clicked_table}' станут неактивными.\nПродолжить?"
        )
        response = confirmation_window.wait_response()

        if not response:
            return

        def perform_edit():
            firmwares = self.get_all_data().get(clicked_table, [])
            try:
                for firmware in firmwares:
                    firmware_id = str(firmware.get("id"))
                    if firmware_id == str(firmware_data[0]):
                        continue
                    if str_to_bool(firmware.get("is_active")):
                        self.api_manager.update_firmware_status(clicked_table, firmware_id, is_active=False, dev_mode=False)

                success = self.api_manager.update_firmware_status(clicked_table, firmware_data[0], is_active=True, dev_mode=False)

                if success:
                    self.after(0, lambda: SuccessMessageBox(
                        self.master,
                        "Статус изменён!"))
                    self.after(0, self.async_reload_data)
                else:
                    self.after(0, lambda: ErrorMessageBox(
                        self.master,
                        "Ошибка изменения!"))
            except Exception as e:
                self.after(0, lambda error=e: ErrorMessageBox(
                    self.master,
                    f"Невозможно изменить стаус.\n{str(error)}"
                ))

        task_manager.add_task(perform_edit)

    def on_treeview_click(self, event):
        selected_tree = event.widget
        region = selected_tree.identify_region(event.x, event.y)

        # получаем все treeview во фрейме
        all_trees = tuple(map(lambda x: x.bootTableFrame.treeview, self.dict_firmwares.values()))

        # снимаем выбор с каждой таблицы, если кликнули не на неё
        for tree in all_trees:
            if selected_tree != tree:
                tree.selection_remove(tree.selection())
                tree.focus_set()
                tree.focus('')

        # Проверяем был ли клик внутри таблицы
        if region in ('cell', 'treeitem'):
            self.clicked_treeview = selected_tree.master.master
            # Выключаем/включаем кнопки через async,
            # так как необходимо написать много кода для управления порядком биндинга.
            # Без async сначала выполняет это событие, а потом только событие на TreeView
            self.after(25, self.check_button)
        else:
            self.command_buttons.turn_off_button("editUsersButton")


    def check_button(self):
        """Включаем кнопку если, выбрана позиция не активная прошивка"""
        if str_to_bool(self.clicked_treeview.selected_item[5]):
            self.command_buttons.turn_off_button("editUsersButton")
        else:
            self.command_buttons.turn_on_button("editUsersButton")
