from gevent.libev.corecext import callback

from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import WarningMessageBox, ConfirmMessageBox, \
    SuccessMessageBox, ErrorMessageBox
from Project.task_manager import task_manager
from Project.AppFrames.AdditionalWindows.AddNewUserWindow import AddNewUserWindow
from Project.AppFrames.AdditionalWindows.EditUserWindow import EditUserWindow
from Project.CustomUiParts.Frames import StandardFrame
from Project.CustomUiParts.Labels import StandardLabel
from Project.CustomUiParts.Windows import VerticalTextContainer, HorizontalButtonContainer
from Project.Tables.CommonCustomTable import CommonCustomTable
from Project.DataClasses.UserInterfaceButtons import allUserButtons, get_prepared_collection
from Project.DataClasses.ColumnsData import allUserDataColumns, get_prepared_collection
from Project.utils import str_to_bool, int_from_str


class UserFrame(StandardFrame):
    """
    Окно для работы с пользователями.
    Тянем экземпляр ApiManager в конструкторе для описания событий при нажатии на кнопки.
    """

    def __init__(self, master):
        super().__init__(master)
        if hasattr(master, "api_manager"):
            self.api_manager = master.api_manager
        self.headers = tuple(map(lambda x: x.name, allUserDataColumns))

        # Итератор наименований столбцов таблицы
        label_data = map(lambda x: (x.header_name, ""), allUserDataColumns)

        # конфигурация окна
        self.grid_propagate(False)
        self.grid_rowconfigure(0, minsize=25)
        self.grid_rowconfigure(1, weight=8)
        self.grid_rowconfigure(1, minsize=1)
        self.grid_rowconfigure(2, minsize=4)
        self.grid_columnconfigure(0, weight=1)

        # фрейм с основными кнопками
        self.userCommandFrame = HorizontalButtonContainer(self, buttons_data=get_prepared_collection(allUserButtons))
        self.userCommandFrame.grid(row=0, column=0, pady=(10, 0))

        # фрейм с таблицей (id, username, role, is_active)
        self.table = CommonCustomTable(self, columns=get_prepared_collection(allUserDataColumns))
        self.table.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        # Текст - заголовок
        self.textdata_header = StandardLabel(self, text="Данные о пользователе:")
        self.textdata_header.grid(row=2, column=0, padx=15, pady=0, sticky='w')

        # фрейм с текстовыми значениями выбранного элемента
        self.label_container = VerticalTextContainer(self, label_data)
        self.label_container.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='nswe')

        # биндим выделение строк
        self.table.treeview.bind("<<TreeviewSelect>>", self.on_select)

        # биндим нажатия кнопок
        self.add_command_to_button("reloadButton", self.reload_users)
        self.add_command_to_button("addUsersButton", self.add_new_user)
        self.add_command_to_button("editUsersButton", self.edit_user)
        self.add_command_to_button("blockUsersButton", lambda: self.change_user_status(False))
        self.add_command_to_button("unblockUsersButton", lambda: self.change_user_status(True))

    def update_table(self, data):
        self.table.update_data(data)

    def on_select(self, event):
        """
        Получаем данные из таблицы в виде кортежа
        event оставляем, так как передается вместе с событием. Без него работать не будет.
        """
        if self.table.on_select(event):
            for i, value in enumerate(self.table.selected_item):
                self.label_container.text_frames[i].set_data(value)
            self.turn_on_buttons_with_select()
        else:
            self.turn_off_buttons_with_select()
            # очищаем лейбы
            for textframe in self.label_container.text_frames:
                textframe.clean_data()

    def turn_on_buttons_with_select(self):
        """Включаем кнопки, которые требуют выбранный элемент в таблице"""
        self.userCommandFrame.turn_on_button("editUsersButton")
        self.userCommandFrame.turn_on_button("blockUsersButton")
        self.userCommandFrame.turn_on_button("unblockUsersButton")

    def turn_off_buttons_with_select(self):
        """Выключаем кнопки, которые требуют выбранный элемент в таблице"""
        self.userCommandFrame.turn_off_button("editUsersButton")
        self.userCommandFrame.turn_off_button("blockUsersButton")
        self.userCommandFrame.turn_off_button("unblockUsersButton")

    def add_command_to_button(self, button_name, new_command):
        """Добавляем новую команду по имени кнопки"""
        self.userCommandFrame.add_command_to_button(button_name, new_command)

    def reload_users(self):
        """
        Событие при нажатии на кнопку Обновить.
        Обновляем состав пользователей в таблице.
        """
        if hasattr(self.master, "async_update_table"):
            self.master.async_update_table(
                data_func=self.api_manager.get_all_users,
                headers=self.headers,
                update_func=self.update_table,
                callback= self.table.scroll_to_last_item)

    def add_new_user(self):
        self.current_window = AddNewUserWindow(self)
        self.check_queue()

    def edit_user(self):
        self.current_window = EditUserWindow(self, self.table.selected_item)
        self.check_queue()

    def change_user_status(self, set_status):
        """Меняем статус пользователя"""
        # пусто в выборе
        if not self.table.selected_item:
            return

        username = self.table.selected_item[1]

        text_data = {
            "blocked": "заблокирован",
            "verb_block": "заблокировать",
        }
        if set_status:
            text_data = {
                "blocked": "активен",
                "verb_block": "разблокировать",
            }

        # пользователь уже заблокирован
        if str_to_bool(self.table.selected_item[3]) == set_status:
            WarningMessageBox(
                self.master,
                f"Пользователь {username}\nуже {text_data["blocked"]}!"
            )
            return

        confrim_window = ConfirmMessageBox(self.master, f"Вы точно хотите {text_data["verb_block"]}\n{username}")
        response = confrim_window.wait_response()

        if response:
            # блокируем кнопки на время выполнения операции
            block_button = self.userCommandFrame.find_button("blockUsersButton")
            ublock_button = self.userCommandFrame.find_button("unblockUsersButton")
            buttons = (block_button, ublock_button)
            [button.turn_off() for button in buttons]

            def perform_block():
                user_id = self.table.selected_item[0]
                try:
                    success = self.api_manager.edit_user_status(user_id, is_active=set_status)
                    if success:
                        self.reload_users()
                        self.after(0, lambda user=username, state=text_data["blocked"]: SuccessMessageBox(
                            self.master,
                            f"Пользователь {user}\nтеперь {state}!"
                        ))
                    else:
                        self.after(0, lambda user=username: ErrorMessageBox(
                            self.master,
                            f"Ошибка изменения статуса\nпользователя {user}!"
                        ))
                except Exception as error:
                    self.after(0, lambda err=error, user=username: ErrorMessageBox(
                        self.master,
                        f"Ошибка при изменении\nстатуса пользователя {user}:\n{str(err)}"
                    ))
                finally:
                    [button.turn_on() for button in buttons]

            task_manager.add_task(target_func=perform_block)
