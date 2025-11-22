from Project.task_manager import task_manager
from Project.CustomUiParts.Frames import TableWithHeaderFrame, StandardFrame
from Project.DataClasses.ColumnsData import allUserDataColumns, allUserHistoryColumns, get_prepared_collection
from Project.utils import convert_timestamp


class UserHistoryFrame(StandardFrame):
    """Основной фрейм с логами работы пользователей"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.api_manager = master.api_manager
        self.headers = tuple(map(lambda x: x.name, allUserDataColumns))

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # таблица пользователей
        self.userTableFrame = TableWithHeaderFrame(
            self,
            header_text="Пользователи",
            columns=get_prepared_collection(allUserDataColumns)
        )
        self.userTableFrame.grid(row=0, column=0, pady=(10, 5), sticky='nsew')

        # таблица с логами по пользователям
        self.userHistoryTableFrame = TableWithHeaderFrame(
            self,
            header_text="История изменений",
            columns=get_prepared_collection(allUserHistoryColumns)
        )
        self.userHistoryTableFrame.grid(row=1, column=0, pady=(5, 10), sticky='nsew')

        # биндим выделение строк
        self.userTableFrame.bootTableFrame.treeview.bind("<<TreeviewSelect>>", self.on_select_user_table)

    def on_select_user_table(self, event):
        """
        Получаем данные из таблицы в виде кортежа.
        По выбранной строке запрашиваем информацию у сервера
        """
        # зачищаем таблицу, возвращаем заголовок
        self.userHistoryTableFrame.clean_data()
        self.userHistoryTableFrame.update_header()

        # отправляем запрос только если только выбрана какая-то строка в таблице
        if self.userTableFrame.bootTableFrame.on_select(event):
            def perform_fetch_userhistory():
                try:
                    user_id, username, *_ = self.userTableFrame.return_selected_item()
                    response = self.api_manager.get_user_history(user_id)
                    self.after(0, lambda u=username: self.userHistoryTableFrame.update_header(u))
                    if response and "detail" not in response:
                        for line in response:
                            if "changed_at" in line:
                                line["changed_at"] = convert_timestamp(line["changed_at"])
                        # вставляем значения в таблицу
                        self.after(0, lambda r=response: self.userHistoryTableFrame.insert_data(r))
                    else:
                        # меняем заголовок если ничего не нашли
                        username += " - ничего не найдено"
                        self.after(0, lambda u=username: self.userHistoryTableFrame.update_header(u))
                except:
                    pass

            task_manager.add_task(perform_fetch_userhistory)
