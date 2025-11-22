from Project.CustomUiParts.TextParts import EditableText
from Project.CustomUiParts.Tooltip import Tooltip
from Project.task_manager import task_manager
from Project.CustomUiParts.Frames import TableWithHeaderFrame, StandardFrame
from Project.DataClasses.ColumnsData import allDevicesDescriptionColumns, get_prepared_collection, \
    allDevicesHistoryColumns
from Project.utils import convert_timestamp, int_from_str


class DeviceHistoryFrame(StandardFrame):
    """Основной фрейм с логами работы пользователей над прошивками"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.api_manager = master.api_manager
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, minsize=25)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Окно поиска
        self.filter_text_input = EditableText(self, "Поиск по UID")
        self.filter_tooltip = Tooltip(self.filter_text_input, "Для поиска нескольких UID введите их через '/'")
        self.filter_text_input.grid(row=0, column=0, pady=(10, 0), padx=10, sticky='nsew')

        # таблица устройств
        self.table = TableWithHeaderFrame(
            self,
            header_text="Устройства",
            columns=get_prepared_collection(allDevicesDescriptionColumns)
        )
        self.table_data = None  # список значений таблицы
        self.headers = self.table.get_table_headers()
        self.table.grid(row=1, column=0, pady=(10, 5), sticky='news')

        # таблица прошивок
        self.deviceHistoryTableFrame = TableWithHeaderFrame(
            self,
            header_text="Историй изменений",
            columns=get_prepared_collection(allDevicesHistoryColumns)
        )
        self.deviceHistoryTableFrame.grid(row=2, column=0, pady=(5, 10), sticky='news')

        # биндинги
        self.table.bootTableFrame.treeview.bind("<<TreeviewSelect>>",
                                                self.on_select_device_table)  # биндим выделение строк
        self.filter_text_input.bind('<KeyRelease>', self.get_device_with_uid)  # биндим поле ввода фильтра

    def async_reload_data(self):
        """Обновляем данные об оборудовании в таблице и записываем значения таблицы в self.table_data"""
        if hasattr(self.master, "async_reload_table"):
            self.master.async_reload_table(
                data_func=self.api_manager.get_all_devices,
                table_frame=self,
                callback=self.table.bootTableFrame.scroll_to_last_item
            )

    def get_device_with_uid(self, event):
        """Фильтруем таблицу по инпуту пользователя"""
        user_input = self.filter_text_input.get_full_text()
        if not self.table_data:
            return
        if user_input:
            # получаем список кодов в списке
            required_uid = user_input.split("/")

            filtered_data = filter(lambda x: x[2] in required_uid, self.table_data)  # x[2] - UID
            self.table.update_data(filtered_data)
        else:
            self.table.update_data(self.table_data)

    def on_select_device_table(self, event):
        """
        Получаем данные из таблицы в виде кортежа.
        По выбранной строке запрашиваем информацию у сервера
        """
        # зачищаем таблицу, возвращаем заголовок
        self.deviceHistoryTableFrame.clean_data()
        self.deviceHistoryTableFrame.update_header()

        # отправляем запрос только если только выбрана какая-то строка в таблице
        if self.table.bootTableFrame.on_select(event):
            def perform_fetch_userhistory():

                _, _, uid, *_ = self.table.return_selected_item()

                self.after(0, lambda u=uid: self.deviceHistoryTableFrame.update_header(u))
                response = self.api_manager.get_device_history(uid)
                if response and "detail" not in response:
                    for line in response:
                        if "changed_at" in line:
                            line["changed_at"] = convert_timestamp(line["changed_at"])
                    # вставляем значения в таблицу
                    self.after(0, lambda r=response: self.deviceHistoryTableFrame.insert_data(r))
                else:
                    # меняем заголовок если ничего не нашли
                    header = f"{uid} - ничего не найдено"
                    self.after(0, lambda u=header: self.deviceHistoryTableFrame.update_header(u))

            task_manager.add_task(target_func=perform_fetch_userhistory)
