from gevent.libev.corecext import callback

from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import SuccessMessageBox, ErrorMessageBox, \
    ConfirmMessageBox
from Project.CustomUiParts.Tooltip import Tooltip
from Project.task_manager import task_manager
from Project.AppFrames.AdditionalWindows.AddNewDeviceWindow import AddNewDeviceWindow
from Project.AppFrames.AdditionalWindows.EditDeviceWindow import EditDeviceWindow
from Project.CustomUiParts.Frames import StandardFrame
from Project.CustomUiParts.TextParts import EditableText
from Project.CustomUiParts.Windows import HorizontalButtonContainer
from Project.DataClasses.ColumnsData import allDevicesDescriptionColumns, get_prepared_collection
from Project.DataClasses.UserInterfaceButtons import allDevicesButtons, get_prepared_collection
from Project.Tables.CommonCustomTable import CommonCustomTable
from Project.utils import int_from_str


class DeviceFrame(StandardFrame):
    """Основной фрейм с логами работы пользователей"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if hasattr(master, "api_manager"):
            self.api_manager = master.api_manager

        self.grid_propagate(False)
        self.grid_columnconfigure(0, minsize=200)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, minsize=50)

        # таблица прошивок
        self.table = CommonCustomTable(
            self,
            columns=get_prepared_collection(allDevicesDescriptionColumns)
        )
        self.headers = self.table.treeview['columns']
        self.table_data = None  # список значений таблицы
        self.table.grid(row=0, column=0, columnspan=2, pady=(10, 2), sticky='news')

        self.CommandButtons = HorizontalButtonContainer(
            self,
            buttons_data=get_prepared_collection(allDevicesButtons)
        )
        self.CommandButtons.grid(row=1, column=0, sticky='w')

        self.filter_text_input = EditableText(self, "Поиск по UID")
        self.filter_tooltip = Tooltip(self.filter_text_input, "Для поиска нескольких UID введите их через '/'")
        self.filter_text_input.grid(row=1, column=1, pady=10, padx=5, sticky='news')

        # биндим кнопки
        self.CommandButtons.add_command_to_button("reloadButton", self.async_reload_data)
        self.CommandButtons.add_command_to_button("addDeviceButton", self.add_device_button_click)
        self.CommandButtons.add_command_to_button("editDeviceButton", self.edit_device_button_click)
        self.CommandButtons.add_command_to_button("removeDeviceButton", self.remove_device_button_click)

        # биндим поле ввода фильтра
        self.filter_text_input.bind('<KeyRelease>', self.get_device_with_uid)
        # биндим выделение строк
        self.table.treeview.bind("<<TreeviewSelect>>", self.on_select)

        self.CommandButtons.turn_off_button("removeDeviceButton")
        self.CommandButtons.turn_off_button("editDeviceButton")

    def async_reload_data(self):
        """Обновляем данные об оборудовании в таблице и записываем значения таблицы в self.table_data"""
        if hasattr(self.master, "async_reload_table"):
            self.master.async_reload_table(
                data_func=self.api_manager.get_all_devices,
                table_frame=self,
                callback=self.table.scroll_to_last_item
            )

    def toggle_remove_button(self, state: bool):
        if state:
            self.CommandButtons.turn_on_button("removeDeviceButton")
        else:
            self.CommandButtons.turn_off_button("removeDeviceButton")

    def on_select(self, event):
        """
        Проверяем выбрал ли пользователь что-то в таблице
        """
        if self.table.on_select(event):
            self.toggle_remove_button(True)
            self.CommandButtons.turn_on_button("editDeviceButton")
        else:
            self.toggle_remove_button(False)
            self.CommandButtons.turn_off_button("editDeviceButton")

    def add_device_button_click(self):
        """Событие при нажатии на кнопку Добавить"""
        self.current_window = AddNewDeviceWindow(self)
        self.check_queue()

    def edit_device_button_click(self):
        """Соыбтие при нажатии на кнопку Изменить"""
        self.current_window = EditDeviceWindow(self, self.table.selected_item)
        self.check_queue()

    def remove_device_button_click(self):
        """Соыбтие при нажатии на кнопку Удалить"""
        # пусто в выборе
        if not self.table.selected_item:
            ErrorMessageBox(self.master,
                            "Ни одно из устройств не выбрано!")
            return

        _, device_name, device_uid, *_ = self.table.selected_item

        # окно для подтверждения удаления
        message_text = f"Вы уверены, что хотите\nудалить устройство:\nИмя: {device_name}\nUID: {device_uid}?"
        confirmation_window = ConfirmMessageBox(self.master, message_text)
        confirmation_window.text.configure(justify='left')
        response = confirmation_window.wait_response()

        if response:
            # блокируем кнопку удаления на время выполнения операции
            self.toggle_remove_button(False)

            def perform_delete_device():
                try:
                    success = self.api_manager.delete_device(device_uid)
                    if success:
                        # всплывающее окно с успехом операции
                        self.after(0, lambda name=device_name, uid=device_uid: SuccessMessageBox(
                            self.master,
                            f"Устройство удалено!\nИмя: {name}\nUID: {uid}"))
                        # обновляем основное окно
                        self.async_reload_data()
                    else:
                        self.after(0, lambda: ErrorMessageBox(self.master, "Ошибка при удалении!"))
                except Exception as error:
                    self.after(0, lambda err=error, device=device_name: ErrorMessageBox(
                        self.master,
                        f"Ошибка при удалении устройства {device}: :\n{str(err)}"
                    ))

            task_manager.add_task(target_func=perform_delete_device)

    def get_device_with_uid(self, event):
        """Фильтруем таблицу по инпуту пользователя"""
        user_input = self.filter_text_input.get_full_text()
        if user_input:
            # получаем список кодов в списке
            required_uid = user_input.split("/")
            filtered_data = filter(lambda x: x[2] in required_uid, self.table_data)  # x[2] - UID
            self.table.update_data(filtered_data)
        else:
            self.table.update_data(self.table_data)
