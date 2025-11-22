from Project.CustomUiParts.AdditionalWindows import TemplateUserInfoWindow
from Project.CustomUiParts.MessageBoxes.SpecialMessageBoxes import ErrorMessageBox
from Project.CustomUiParts.TextFrames import SwitchFrame
from Project.settings import SETUP_PASSWORD
from Project.task_manager import task_manager
from Project.utils import str_to_bool


class EditUserWindow(TemplateUserInfoWindow):
    """Всплывающее дополнительное окно для редактирования пользователя"""

    def __init__(self, master, userdata: tuple):
        super().__init__(master, "Редактировать данные пользователя", "Изменить")
        self.add_command_to_main_button(self.edit_user)

        # исходные параметры о пользователе
        self.user_id = userdata[0]
        self.current_username = userdata[1]
        self.current_role = userdata[2]
        self.current_status = str_to_bool(userdata[3])

        self.set_current_userdata(
            username=self.current_username,
            role=self.current_role,
            is_active=self.current_status
        )
        self.password_switch = SwitchFrame(self, "Изменить пароль", "")
        self.password_switch.status_switch.configure(command=self.status_change_password)
        self.password_switch.set_data(False)

        self.grid_columnconfigure(0, weight=1)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        self.new_name.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.password_switch.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        self.new_password.grid(row=2, column=0, padx=10, pady=(5, 2), sticky='e')
        self.status_frame.grid(row=3, column=0, sticky='nswe')
        self.status_switch.grid(row=4, column=0, padx=20, pady=5, sticky='w')

        self.user_role.grid(row=5, column=0, padx=20, pady=5, sticky='w')
        self.create_button.grid(row=6, column=0, padx=50, pady=5, sticky='we')
        self.disable_password_objects()

        # дополнительная проверка свитча и комбобокса для активации кнопки
        for obj in (self.status_switch.status_switch, self.user_role.comboBox):
            obj.configure(command=self.validate_userinput)

    def set_current_userdata(self, username: str, role: str, is_active: bool):
        self.new_name.set_data(username)
        self.user_role.set_data(role)
        self.status_switch.set_data(is_active)

    def status_change_password(self):
        # запускаем валидацию, чтобы активировать кнопку
        self.validate_userinput()
        # проверяем положение свитча
        if self.password_switch.get_data() == 0:
            self.disable_password_objects()
        else:
            self.enable_password_objects()

    def disable_password_objects(self):
        # обновление ввода пароля
        self.new_password.clean_data()
        self.new_password.change_placeholder_text("Пароль не изменится")
        self.new_password.text_result.configure(state='disabled')
        # блокировка кнопки генерации пароля
        self.generate_password_btn.configure(state='disabled')
        # обновление статуса пароля
        self.password_status.configure(text="Пароль не изменится")
        # обновляем tooltip
        self.gnrt_password_tooltip.change_text("Пароль изменить нельзя")

    def enable_password_objects(self):
        # обновление ввода пароля
        self.new_password.text_result.configure(state='normal')
        self.new_password.change_placeholder_text("Введите новый пароль")
        # блокировка кнопки генерации пароля
        self.generate_password_btn.configure(state='normal')
        # обновление статуса пароля
        self.password_status.configure(text=SETUP_PASSWORD)
        # обновляем tooltip
        self.gnrt_password_tooltip.change_text("Сгенерировать пароль")

    # функция валидации, которая проверяет, есть ли что-нибудь в Entries, и тогда активирует кнопку
    def validate_userinput(self, event=None):
        # проверяем нужно ли изменить пароль
        password = True
        if self.password_switch.get_data() == 1:
            password = self.validate_password(event)

        login = self.new_name.get_data()
        button_state = "disabled"
        if password and login:
            button_state = "normal"
        self.create_button.configure(state=button_state)

    def edit_user(self):
        # словарь собирающий данные для изменения
        self.create_button.turn_off()
        new_data = {}

        # получаем обновленные данные
        new_username = self.new_name.get_data()
        new_password = self.new_password.get_data() if self.password_switch.get_data() else None
        new_status = self.status_switch.get_data()
        new_role = self.user_role.get_data()

        # проверяем что необходимо добавить
        if new_username != self.current_username:
            new_data["username"] = new_username
        if new_password:
            new_data["password"] = new_password
        if new_role != self.current_role:
            new_data["role"] = new_role
        if new_status != self.current_status:
            new_data["is_active"] = new_status

        # запускаем изменение пользователя, если нашлись какие-либо изменения
        if new_data:
            def perform_edit():
                try:
                    success = self.api_manager.edit_user(self.user_id, **new_data)
                    if success:
                        if hasattr(self.master, "reload_users"):
                            self.master.reload_users()
                        if hasattr(self.master, "message_queue"):
                            self.master.message_queue.put("close")
                        self.master.message_text = f"Пользователь\n{new_username}\nизменён!"
                    else:
                        self.after(0, lambda: ErrorMessageBox(
                            self,
                            "Ошибка при изменении!"
                        ))
                        self.after(0, lambda: self.create_button.turn_on)
                except Exception as error:
                    self.after(0, lambda err=error: ErrorMessageBox(
                        self,
                        f"Ошибка при редактировании\nпользователя:\n{str(err)}"
                    ))
                    self.after(0, lambda: self.create_button.turn_on)

            task_manager.add_task(target_func=perform_edit)
        else:
            self.after(0, lambda: ErrorMessageBox(
                self,
                f"Изменений не обнаружено"
            ))
