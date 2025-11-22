from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox
from Project.task_manager import task_manager
from Project.CustomUiParts.AdditionalWindows import DeviceWindowTemplate
from Project.utils import str_to_bool


class EditDeviceWindow(DeviceWindowTemplate):
    """
    Всплывающее дополнительное окно для редактирования данных устройства
    device_datd : (id, name, uid, production, boot_flash, app_flash, activation)
    """

    def __init__(self, master, device_data: tuple):
        super().__init__(master, "Изменить устройство", "Изменить")
        # выставляем исходные данные, enumerate для перевода текстовых полей в булевые
        # кортеж (id, name, uid, production, boot_flash, app_flash, activation)
        data = device_data[:3] + device_data[4:]  # убираем 3 лишних атрибута с инпута
        # переводим необходимые параметры в буелвые значения
        self.device_data = tuple(map(
            lambda tuple_value: tuple_value[1] if tuple_value[0] < 3 else str_to_bool(tuple_value[1]),
            enumerate(data)
        ))
        # кнопка
        self.command_button.configure(
            command=self.edit_device
        )

        # устанавливаем исходные значения
        self.default_data()

        # биндим пользоватеский ввод
        self.device_name_input.text_result.bind('<KeyRelease>', self.check_userinput)
        self.uid_input.text_result.bind('<KeyRelease>', self.check_userinput)
        for obj in self.switches:
            obj.status_switch.configure(command=self.check_userinput)

    def edit_device(self):
        # проверяем есть ли api_manager у окна для коннекта
        if not hasattr(self, "api_manager"):
            return

        self.command_button.turn_off()
        userinput = self.get_all_userdata()

        updated_data = {}
        if len(userinput[1]) != 24:  # проверяем чтобы UID был ровно 24 символа
            ErrorMessageBox(
                self,
                f"UID должен содержать\nровно 24 символа!\nСейчас: {len(userinput[1])}"
            )
            return

        dict_keys = ("name", "uid", "production", "boot_flash", "app_flash", "activation")
        # исходные данные без ID для поиска изменений
        default_data = self.device_data[1:]
        for index, attribute in enumerate(userinput):
            if attribute != default_data[index]:
                updated_data[dict_keys[index]] = attribute

        # функция изменения параметров устройства
        def perform_edit():
            try:
                success = self.api_manager.edit_device(self.device_data[2], **updated_data)
                if success:
                    # уведомляем основной поток, что можно закрыть окно
                    if hasattr(self.master, "message_queue"):
                        self.master.message_queue.put("close")
                    self.master.message_text = f"Устройство под номером\n{userinput[1]}\nизменено!"  # передаем сообщение
                    # обновляем основную таблицу если возможно
                    if hasattr(self.master, "async_reload_data"):
                        self.master.async_reload_data()
                else:
                    self.after(0, lambda: ErrorMessageBox(
                        self,
                        "Ошибка при редактировании\nпараметров устройства!"))
            except Exception as e:
                self.after(0, lambda error=e: ErrorMessageBox(
                    self,
                    f"Неизвестная ошибка!\n{error}"))

        task_manager.add_task(target_func=perform_edit)

    def default_data(self):
        """Устанавливаем исходные данные"""
        # скидываем валидацию с uid_input, чтобы редактировать поле
        self.uid_input.delete_validate_rule()
        self.uid_input.set_data(self.device_data[2])
        self.uid_input.add_validate_rule(self.validate_uid)

        self.device_name_input.set_data(self.device_data[1])

        # кортеж свитчей для прохождения
        default_switches = self.device_data[3:]

        for index, switch in enumerate(self.switches):
            switch.set_data(default_switches[index])

    def is_different_from_start(self):
        """Разница между исходным инпутом и новым"""
        user_input = self.get_all_userdata()
        default_data = self.device_data[1:]
        return user_input != default_data

    def allowed_uid_length(self):
        """Проверяем длину UID"""
        return len(self.uid_input.get_data()) == 24

    def anything_in_name_entry(self):
        """Что-то должно быть вписано в device_name"""
        return bool(self.device_name_input.get_data())

    def check_userinput(self, event=None):
        """
        Проверяем пользовательский ввода, если все ок, то включаем кнопку.
        Также должны быть хоть какие-то изменения от первоночальных данных
        """
        # функции для проверки
        check_funcs = (self.allowed_uid_length, self.anything_in_name_entry, self.is_different_from_start)
        if all(map(lambda x: x(), check_funcs)):
            self.command_button.turn_on()
        else:
            self.command_button.turn_off()
