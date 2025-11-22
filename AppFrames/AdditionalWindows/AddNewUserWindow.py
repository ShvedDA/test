from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox
from Project.task_manager import task_manager
from Project.CustomUiParts.AdditionalWindows import TemplateUserInfoWindow


class AddNewUserWindow(TemplateUserInfoWindow):
    """Всплывающее дополнительное окно для создания нового пользователя"""

    def __init__(self, master):
        super().__init__(master, "Добавить пользователя", "Добавить")
        self.add_command_to_main_button(self.add_user)
        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)
        self.new_name.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.new_password.grid(row=1, column=0, padx=10, pady=(5, 2), sticky='e')
        self.status_frame.grid(row=2, column=0, sticky='nswe')
        self.status_switch.grid(row=3, column=0, padx=20, pady=5, sticky='w')
        self.user_role.grid(row=4, column=0, padx=20, pady=5, sticky='w')
        self.create_button.grid(row=5, column=0, padx=50, pady=5, sticky='we')

    def add_user(self):
        """Команда для создания нового пользователя"""
        userinput = self.read_userinput()
        self.create_button.turn_off()

        def perform_add_user():
            try:
                response = self.api_manager.create_user(*userinput)
                if response:
                    if hasattr(self.master, "reload_users"):
                        self.master.reload_users()
                    if hasattr(self.master, "message_queue"):
                        self.master.message_queue.put("close")
                    self.master.message_text = f"Пользователь {userinput[0]}\nуспешно создан!"
                else:
                    self.after(0, lambda: ErrorMessageBox(
                        self,
                        "Ошибка при создании\nпользователя!"
                    ))
                    self.after(0, lambda: self.create_button.turn_on)
            except Exception as error:
                self.after(0, lambda err=error: ErrorMessageBox(
                    self,
                    f"Не удалось обновить данные:\n{str(err)}"
                ))
                self.after(0, lambda: self.create_button.turn_on)

        task_manager.add_task(perform_add_user)
