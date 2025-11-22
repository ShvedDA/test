from Project.task_manager import task_manager
from Project.CustomUiParts.Frames import TableWithHeaderFrame, StandardFrame
from Project.DataClasses.ColumnsData import allFirmwareColumns, get_prepared_collection, allUserHistoryColumns
from Project.settings import FIRMWARE_TYPES
from Project.utils import convert_timestamp


class FirmwareHistoryFrame(StandardFrame):
    """
    Окно для просмотра логов работы с прошивками
    """

    def __init__(self, master, dev_mode: bool = False, **kwargs):
        super().__init__(master, **kwargs)
        self.api_manager = master.api_manager
        self.dev_mode = dev_mode  # режим работы: True - разработка, False - релиз
        self.grid_propagate(False)
        # конфигурируем фрейм
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # таблица прошивок
        self.firmwareTableFrame = TableWithHeaderFrame(
            self,
            header_text="Прошивки",
            columns=get_prepared_collection(allFirmwareColumns)
        )
        self.headers = self.firmwareTableFrame.get_table_headers()  # заголовки таблицы
        self.firmwareTableFrame.grid(row=0, column=0, pady=(10, 5), sticky='nsew')

        # таблица логов по прошивкам
        self.historyTableFrame = TableWithHeaderFrame(
            self,
            header_text="История изменений",
            columns=get_prepared_collection(allUserHistoryColumns)
        )
        self.historyTableFrame.grid(row=1, column=0, pady=(5, 10), sticky='nsew')

        # биндим выделение строк
        self.firmwareTableFrame.bootTableFrame.treeview.bind("<<TreeviewSelect>>", self.on_select_firmware_table)

    def on_select_firmware_table(self, event):
        """
        Получаем данные из таблицы в виде кортежа.
        По выбранной строке запрашиваем информацию у сервера
        """
        # зачищаем таблицу, возвращаем заголовок
        self.historyTableFrame.clean_data()
        self.historyTableFrame.update_header()

        # отправляем запрос только если только выбрана какая-то строка в таблице
        if self.firmwareTableFrame.bootTableFrame.on_select(event):
            def perform_fetch_userhistory():

                firmware_id, firmware_type, *_ = self.firmwareTableFrame.return_selected_item()

                for key, value in FIRMWARE_TYPES.items():
                    if value == firmware_type:
                        firmware_type = key
                        break

                firmware_type_ru = FIRMWARE_TYPES[firmware_type]
                header = f"{firmware_id}/{firmware_type_ru}"
                self.after(0, lambda u=header: self.historyTableFrame.update_header(u))
                response = self.api_manager.get_firmware_history(firmware_type, firmware_id, self.dev_mode)
                if response and "detail" not in response:
                    for line in response:
                        if "changed_at" in line:
                            line["changed_at"] = convert_timestamp(line["changed_at"])
                    # вставляем значения в таблицу
                    self.after(0, lambda r=response: self.historyTableFrame.insert_data(r))
                else:
                    # меняем заголовок если ничего не нашли
                    header += " - ничего не найдено"
                    self.after(0, lambda u=header: self.historyTableFrame.update_header(u))

            task_manager.add_task(target_func=perform_fetch_userhistory)
