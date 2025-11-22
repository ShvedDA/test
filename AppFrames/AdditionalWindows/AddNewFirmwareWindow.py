from datetime import datetime

from tomlkit import value

from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox
from Project.task_manager import task_manager
from Project.CustomUiParts.AdditionalWindows import FirmwareWindowTemplate
from Project.utils import str_to_bool


class AddNewFirmwareWindow(FirmwareWindowTemplate):
    """Всплывающее дополнительное окно для создания нового устройства"""

    def __init__(self, master, firmware_data, dev_mode):
        super().__init__(master, "Добавление прошивки", "Добавить", firmware_data, dev_mode)
        # выставляем объекты
        self.type_frame.grid(row=0, column=0, padx=5, pady=(5, 2), sticky="e")
        self.version_frame.grid(row=1, column=0, padx=5, pady=(2, 0), sticky="e")
        self.version_description_label.grid(row=2, column=0, padx=(80, 0), pady=(2, 0), sticky="nwe")
        self.stage_frame.grid(row=3, column=0, padx=32, pady=2, sticky="w")
        if dev_mode is True:
            self.stage_frame.set_data(True)
        else:
            self.stage_frame.set_data(False)
        self.stage_frame.block_switch(True)
        self.state_frame.grid(row=4, column=0, padx=32, pady=2, sticky="w")
        self.file_frame.grid(row=5, column=0, padx=(5, 10), pady=2, sticky="e")
        self.description_frame.grid(row=6, column=0, padx=5, pady=2, sticky="e")
        self.information_frame.grid(row=7, column=0, padx=5, pady=2, sticky="e")

        self.command_button.configure(command=self.add_firmware)  # прописываем команду

    def add_firmware(self):
        self.command_button.turn_off()
        user_data = self.get_all_userdata()

        def perform_add():
            try:
                success = True
                if "firmware_type" not in user_data:
                    return

                # ищем все прошивки выбранного типа
                for f_type in user_data["firmware_type"]:
                    # если добавляем прошивку активную, то необходимо деактивировать остальные выбранного типа
                    if user_data.get("is_active", False):
                        firmwares_to_deactivate = filter(
                            lambda x: str_to_bool(x.get("is_active", False)),
                            self.firmwaredata.get(f_type, [])
                        )
                        # отключаем отфильтрованные прошивки
                        for firmware in firmwares_to_deactivate:
                            self.api_manager.update_firmware_status(f_type, firmware["id"], False)

                    # добавляем прошивку
                    result = self.api_manager.add_firmware(
                        firmware_type=f_type,
                        version=user_data["version"],
                        release_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                        description=user_data["description"],
                        info=user_data["info"],
                        is_active=user_data["is_active"],
                        dev_mode=user_data["dev_mode"],
                        file_path=user_data["file_path"]
                    )

                    if not result:  # выходим если ошибка во время выполнения
                        success = False
                        break

                if success:
                    if hasattr(self.master, "async_reload_data"):
                        self.after(0, self.master.async_reload_data)
                    if hasattr(self.master, "message_queue"):
                        self.master.message_queue.put("close")
                    self.master.message_text = f"Прошивка {user_data["version"]}\nдобавлена!"
                else:
                    self.after(0, lambda: ErrorMessageBox(
                        self.master,
                        "Невозможно добавить прошивку!"))
            except Exception as e:
                self.after(0, lambda error=e: ErrorMessageBox(
                    self.master,
                    f"Ошибка во время добавления прошивки!\n{str(error)}"))

        task_manager.add_task(perform_add)
