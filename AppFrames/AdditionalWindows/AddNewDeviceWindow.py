from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox
from Project.task_manager import task_manager
from Project.CustomUiParts.AdditionalWindows import DeviceWindowTemplate


class AddNewDeviceWindow(DeviceWindowTemplate):
    """Всплывающее дополнительное окно для создания нового устройства"""

    def __init__(self, master):
        super().__init__(master, "Добавить устройство", "Добавить")
        self.can_be_closed = False

        # кнопка
        self.command_button.configure(command=self.create_device)

        # биндим пользоватеский ввод
        self.device_name_input.text_result.bind('<KeyRelease>', self.check_userinput)
        self.uid_input.text_result.bind('<KeyRelease>', self.check_userinput)

    def check_userinput(self, event):
        """Проверяем пользовательский ввода, если все ок, то включаем кнопку"""

        if self.device_name_input.get_data() and len(self.uid_input.get_data()) == 24:
            self.command_button.turn_on()
        else:
            self.command_button.turn_off()

    def create_device(self):
        """Событие при нажатии на кнопку"""

        # проверяем есть ли api_manager у окна для коннекта
        if not hasattr(self, "api_manager"):
            return

        self.command_button.turn_off()
        userdata = self.get_all_userdata()
        uid = userdata[1]

        if len(uid) != 24:  # проверяем чтобы UID был ровно 24 символа
            ErrorMessageBox(self, f"UID должен содержать ровно 24 символа!\nСейчас: {len(uid)}")
            return

        # функция добавления нового устройства
        def perform_create():
            try:
                success = self.api_manager.create_device(*userdata)
                if success:
                    # обновляем основную таблицу если возможно
                    if hasattr(self.master, "async_reload_data"):
                        self.master.async_reload_data()
                    # уведомляем основной поток, что можно закрыть окно
                    if hasattr(self.master, "message_queue"):
                        self.master.message_queue.put("close")
                    self.master.message_text = f"Устройство под номером\n{uid}\nсоздано!"  # передаем сообщение
                else:
                    self.after(0, lambda: ErrorMessageBox(self, "Ошибка создания!"))
                    self.after(0, lambda: self.command_button.turn_on)
            except Exception as e:
                self.after(0, lambda error=e: ErrorMessageBox(self,
                                                              f"Неизвестная ошибка!\n{error}"))
                self.after(0, lambda: self.command_button.turn_on)

        task_manager.add_task(target_func=perform_create)
