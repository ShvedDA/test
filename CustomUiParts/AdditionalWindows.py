import re
from tkinter import filedialog

from customtkinter import CTkToplevel, CTkFrame

from Project.CustomUiParts.Buttons import KeyButton, CustomUserButtons, StandardButton
from Project.CustomUiParts.Labels import DescriptionLabel
from Project.CustomUiParts.TextFrames import EditableTextFrame, SwitchFrame, ComboBoxFrame, TextBlockedFrame
from Project.CustomUiParts.Tooltip import Tooltip
from Project.Services.ValidationsRules import validate_login_name
from Project.settings import SMALL_WINDOW_WIDTH, SMALL_WINDOW_HEIGHT, IMAGES_DIR, SETUP_PASSWORD, USERS_ROLES, \
    PASSWORD_DIGITS, PASSWORD_SPECIAL_CHARS, READY_PASSWORD, POSSIBLE_FIRMWARE_TYPES_REL, POSSIBLE_FIRMWARE_TYPES_DEV, \
    FONT_ADDITIONAL, POSSIBLE_FIRMWARE_TYPES_REL
from Project.utils import resource_path, generate_secure_password, relative_center


class AdditionalWindow(CTkToplevel):
    """
    Класс для вспомогательных окон
    """

    def __init__(self, master, window_name, width=SMALL_WINDOW_WIDTH, height=SMALL_WINDOW_HEIGHT):
        super().__init__(master)
        # выставляем api_manager, если он есть у родительского окна
        # Сделано для тестов, чтобы была возможность запустить без api_manager
        if hasattr(master, "api_manager"):
            self.api_manager = master.api_manager
        self.set_geometry(master, width, height)
        self.title(window_name)
        self.resizable(False, False)
        self.grab_set()
        # Иконка добавляется через async так, как есть баг во фреймворке, описан гите:
        # https://github.com/TomSchimansky/CustomTkinter/issues/1163
        self.after(200, lambda: self.iconbitmap(resource_path(IMAGES_DIR / "iconRus.ico")))

    def set_geometry(self, master, window_width, window_height):
        root = self.master.winfo_toplevel()  # определяем главное родительское окно
        self.update_idletasks()  # обновляем UI
        # определяем параметры для расчета
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        x, y = relative_center(
            root_x,
            root_y,
            root_width,
            root_height,
            window_width,
            window_height
        )
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")


class TemplateUserInfoWindow(AdditionalWindow):
    """Шаблон для окна работой над информацией о пользователе"""

    def __init__(self, master, window_name, button_text):
        super().__init__(master, window_name)

        allowed_symbols = (self.register(validate_login_name), "%S")
        self.new_name = EditableTextFrame(self, "Логин", "Введите логин", validate_rule=allowed_symbols)
        self.new_password = EditableTextFrame(self, "Пароль", "Введите пароль", validate_rule=allowed_symbols)
        # отдельный фрейм для вставки кнопки генерации пароля и текста
        self.status_frame = CTkFrame(self, fg_color="transparent", bg_color="transparent")
        # minsize чтобы родительский фрейм не изменялся при изменении статуса
        self.status_frame.grid_rowconfigure(0, minsize=50)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(1, minsize=50)

        # описание введенного пароля
        self.password_status = DescriptionLabel(self.status_frame, SETUP_PASSWORD)
        self.password_status.grid(row=0, column=0, padx=10, sticky='we')

        # кнопка генерации пароля
        self.generate_password_btn = KeyButton(self.status_frame, command=self.generate_password)
        self.gnrt_password_tooltip = Tooltip(self.generate_password_btn, "Сгенерировать пароль")
        self.generate_password_btn.grid(row=0, column=1, padx=(10, 20), pady=(5, 5), sticky='we')

        # статус свитч
        self.status_switch = SwitchFrame(self, "Статус", "Активен")

        self.user_role = ComboBoxFrame(self, "Роль", USERS_ROLES, USERS_ROLES[2])
        self.create_button = CustomUserButtons(self,
                                               name="create_button",
                                               text=button_text,
                                               state='disabled')

        # коллекция для работы с введенными данными пользователя
        self.fields = (self.new_name, self.new_password, self.user_role, self.status_switch)

        for entry in (self.new_name.text_result, self.new_password.text_result):
            entry.bind("<KeyRelease>",
                       lambda e: self.validate_userinput(e))

    def add_command_to_main_button(self, newcommand: callable):
        """Добавляем команду к кнопке"""
        self.create_button.configure(command=newcommand)

    def read_userinput(self):
        """Возвращаем инпут пользователя кортежом: (логин, пароль, статус, роль)"""
        return tuple(textframe.get_data() for textframe in self.fields)

    def clean_userinput(self):
        """Очищаем инпут пользователя для избегания создания дублей"""
        for textframe in self.fields:
            textframe.clean_data()

    def generate_password(self):
        """Генерируем пароль в поле 'новый пароль'"""
        if self.new_password.get_data():
            self.new_password.clean_data()
        password = generate_secure_password(PASSWORD_DIGITS, PASSWORD_SPECIAL_CHARS)
        self.new_password.set_data(password)
        self.validate_userinput(self)

    # функция валидации, которая проверяет, есть ли что-нибудь в Entries, и тогда активирует кнопку
    def validate_userinput(self, event=None):
        password = self.validate_password(event)
        login = self.new_name.get_data()

        button_state = "disabled"
        if password and login:
            button_state = "normal"
        self.create_button.configure(state=button_state)

    # функция проверки пароля
    def validate_password(self, event):
        """Проверка пароля на соблюдение требований."""
        password = self.new_password.get_data()

        # Проверяем все условия
        has_digit = any(c in PASSWORD_DIGITS for c in password)
        has_special = any(c in PASSWORD_SPECIAL_CHARS for c in password)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_min_length = len(password) >= 8

        is_valid = all([has_digit, has_special, has_lower, has_upper, has_min_length])

        if is_valid:
            self.password_status.configure(text=READY_PASSWORD)
        else:
            self.password_status.configure(text=SETUP_PASSWORD)

        return is_valid


class DeviceWindowTemplate(AdditionalWindow):
    """Всплывающее дополнительное окно для работы с устройством"""

    def __init__(self, master, window_name, button_text):
        super().__init__(master, window_name)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, minsize=15)
        for i in range(4):
            self.grid_rowconfigure(3 + i, minsize=20)
        self.grid_rowconfigure(7, weight=1)

        # название устройства
        self.device_name_input = EditableTextFrame(self, "Название", "Введите название")
        self.device_name_input.change_width(280)
        self.device_name_input.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="SE")

        # UID устройства
        self.validate_uid = (self.register(self.validate_uid_input), "%S", "%P")
        self.default_uid_text = "Введите номер UID"
        self.uid_input = EditableTextFrame(self, "UID", self.default_uid_text, validate_rule=self.validate_uid)
        self.uid_input.change_width(280)
        self.uid_input.grid(row=1, column=0, padx=10, columnspan=2, sticky="SE")

        # Описание правил валидации ввода в поле UID устройства
        self.description = DescriptionLabel(self, "24 символа (0-9, A-F)")
        self.description.grid(row=2, column=0, padx=10, pady=(5, 20), columnspan=2)

        # свитч производствао
        self.production_switch = SwitchFrame(self, "Производство", "Да", default=False)
        # свитч Boot flash
        self.bootflash_switch = SwitchFrame(self, "Boot Flash", "Да", default=False)
        # свитч App Flash
        self.appflash_switch = SwitchFrame(self, "App Flash", "Да", default=False)
        # свитч Активация
        self.activation_switch = SwitchFrame(self, "Активация", "Да", default=False)
        # все свитчи
        self.switches = (
            self.production_switch,
            self.bootflash_switch,
            self.appflash_switch,
            self.activation_switch
        )
        self.setup_switches(3)

        # кнопка
        self.command_button = CustomUserButtons(
            self,
            "commandButton",
            button_text,
            state='disabled'
        )
        self.command_button.grid(row=7, column=0, padx=10, pady=20, columnspan=2)

    def setup_switches(self, start_index):
        """Ставим свитчи"""
        for index, switch in enumerate(self.switches):
            switch.grid(row=start_index + index, column=0, sticky="SE")

    def validate_uid_input(self, char, new_text):
        """Функция валидации для UID"""
        # БАГ.
        # При FocusIn на пустой entry без пользовательского текста,
        # фреймворк отправляет placeholder_text в char атрибут.
        # Поэтому нужно почистить вручную и только через async
        if char == self.default_uid_text:
            self.after(0, lambda: self.uid_input.clean_data)
            # переписываем значение атрибута char, иначе не работает также
            char = ""
        # дальше все как обычно
        if char == "":
            return True
        # текст не более 24 символов
        if len(new_text) > 24:
            return False
        # regex правило для UID
        return bool(re.fullmatch(r"^[0-9A-F]*$", char))

    def get_all_userdata(self):
        """
        Получаем все данные в виде кортежа:
        (name, uid, production, boot_flash, app_flash, activation)
        """
        self.device_name_input.split_text()
        user_input = (self.device_name_input, self.uid_input, *self.switches)
        return tuple(map(lambda x: x.get_data(), user_input))


class FirmwareWindowTemplate(AdditionalWindow):
    """
    Всплывающее дополнительное окно для работы с прошивками
    firmwaredata : {Тип прошивки: кортеж с номерами прошивок}
    """

    def __init__(self, master, window_name, button_text, firmwaredata: dict, dev_mode):
        super().__init__(master, window_name, 400, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, minsize=35)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)

        self.firmwaredata = firmwaredata

        # тип прошивки, по дефолту: Загрузчик
        if dev_mode is True:
            firmware_types = tuple(POSSIBLE_FIRMWARE_TYPES_DEV.keys())
            self.type_frame = ComboBoxFrame(
                self,
                "Тип",
                firmware_types,
                firmware_types[0]
            )
        else:
            firmware_types = tuple(POSSIBLE_FIRMWARE_TYPES_REL.keys())
            self.type_frame = ComboBoxFrame(
                self,
                "Тип",
                firmware_types,
                firmware_types[0]
            )
        self.type_frame.comboBox.configure(
            width=300,
            state="readonly",
            command=lambda x: self.validate_version_input()
        )

        # правило проверки
        self.validate_version_entry = (self.register(self.validate_version_textnumber), "%S", "%P")
        # версия
        self.default_firmware_number_text = "XX.XX.XX"
        self.version_frame = EditableTextFrame(
            self,
            "Версия",
            self.default_firmware_number_text,
            validate_rule=self.validate_version_entry,
        )
        self.version_is_okay = False

        # описание ввода номера прошивки
        self.default_label = "Версия должна быть в формате XX.XX.XX\n(например, 1.1.11)"
        self.version_description_label = DescriptionLabel(self, text=self.default_label)

        # статутс прошивки
        self.state_frame = SwitchFrame(
            self,
            "Статус",
            "Сделать активной",
            False
        )

        #стадия прошивки
        self.stage_frame = SwitchFrame(
            self,
            "Стадия",
            "Разработка",
            False
        )

        # файл прошивки
        self.file_frame = CTkFrame(self, fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.file_entry = TextBlockedFrame(self.file_frame, "Файл")
        self.file_entry.text_result.configure(
            font=FONT_ADDITIONAL,
            border_width=2,
            width=226
        )
        self.file_entry.grid(row=0, column=0, sticky="nsew")
        self.file_button = StandardButton(
            self.file_frame,
            "Выбрать",
            width=50,
            command=self.select_firmware_file
        )
        self.file_button.grid(row=0, column=1, sticky="e")

        # описание прошивки
        self.description_frame = EditableTextFrame(self, "Описание", "Введите текст")

        # информация о прошивке
        self.information_frame = EditableTextFrame(self, "Инф-ция", "Введите текст")

        # перечислелние фреймов для пользовательского ввода
        self.user_dataframes = (
            self.type_frame,
            self.version_frame,
            self.state_frame,
            self.stage_frame,
            self.file_entry,
            self.description_frame,
            self.information_frame
        )

        # кнопка команды
        self.command_button = CustomUserButtons(
            self,
            "commandButton",
            button_text,
            state='disabled',
        )
        self.command_button.grid(row=8, column=0, padx=25, pady=10)

        # биндим поля
        for entry in (self.description_frame, self.information_frame):
            entry.text_result.bind("<KeyRelease>", lambda e: self.check_user_input(e))

        self.type_frame.bind("<KeyRelease>", self.validate_version_input)
        self.version_frame.text_result.bind("<KeyRelease>", self.validate_version_input)

    def validate_version_textnumber(self, char, new_text):
        """Функция валидации для версии прошивки"""
        # БАГ. При FocusIn на пустой entry без пользовательского текста,
        # фреймворк отправляет placeholder_text в char атрибут.
        if char == self.default_firmware_number_text:
            return True

        # разрешение удаления символа
        if char == "" and new_text == "":
            return True

        # Ввод ввида "XX.XX.XX" = 8 символов
        if len(new_text) > 8:
            return False

        # проверка символов
        if bool(re.fullmatch(r"^[0-9.]*$", char)):
            return True

        return False

    def check_version_input(self):
        """Проверяем правильно ли заполнено поле ввода версии прошивки"""
        version_pattern = r"^\d{1,2}\.\d{1,2}\.\d{1,2}$"
        return re.match(version_pattern, self.version_frame.get_data())

    def validate_version_input(self, event=None, dev_mode=None):
        """Проверка номера версии прошивки"""
        firmware_number: str = self.version_frame.get_data()
        # если ничего нет в номере версии
        if firmware_number == "":
            self.set_default_label()
            self.version_is_okay = False
            self.check_user_input(event)
            return

        if not self.check_version_input():
            self.update_description_text("Неверный формат версии! Используйте XX.XX.XX", False)
            self.version_is_okay = False
            self.check_user_input(event)
            return

        # чистим номер прошивки
        parts = firmware_number.split(".")
        firmware_number = ".".join(str(int(part)) for part in parts)

        # получаем текущий тип прошивки
        firmware_type = self.type_frame.get_data()

        # создаем список прошивок, которые необходимо проверить на дубли
        firmware_types_to_check = []
        if dev_mode is True:
            firmware_types_to_check.extend(POSSIBLE_FIRMWARE_TYPES_DEV[firmware_type])
        else:
            firmware_types_to_check.extend(POSSIBLE_FIRMWARE_TYPES_REL[firmware_type])

        is_exist = False

        for f_type in firmware_types_to_check:
            firmwares_for_type = map(lambda x: x.get("version", ""), self.firmwaredata.get(f_type, []))
            if firmware_number in firmwares_for_type:
                is_exist = True
                break

        if is_exist:
            self.update_description_text(
                f"Версия {firmware_number} уже существует для {firmware_type}!",
                False
            )

        else:
            self.update_description_text(
                "Версия доступна",
                True
            )
        self.version_is_okay = not is_exist
        self.check_user_input(event)

    def check_user_input(self, event):
        """Проверям наличие пользовательского ввода для активации кнопки"""
        entries_to_check = (self.file_entry, self.description_frame, self.information_frame)

        entries = all(map(lambda x: x.get_data(), entries_to_check))
        if entries and self.version_is_okay:
            self.command_button.turn_on()
        else:
            self.command_button.turn_off()

    def select_firmware_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл прошивки",
            filetypes=[("Binary files", "*.bin")]
        )
        if file_path:
            self.file_entry.set_data(file_path)
        self.validate_version_input(None)

    def get_all_userdata(self):
        """
        Получаем все данные в виде кортежа:
        (type, version, is_active, file_path, description, info)
        """
        dict_keys = ("firmware_type", "version", "is_active", "dev_mode", "file_path", "description", "info")
        result_dict = {key: value.get_data() for key, value in zip(dict_keys, self.user_dataframes)}

        # переименовываем тип прошивки в стандартный
        result_dict["firmware_type"] = POSSIBLE_FIRMWARE_TYPES_REL[result_dict["firmware_type"]]

        # обновление номера
        #parts = result_dict["version"].split(".")
        #result_dict["version"] = ".".join(str(int(part)) for part in parts)

        return result_dict

    def set_default_label(self):
        """Выставляем стандартное описание"""
        text = self.default_label
        self.version_description_label.configure(
            text=text,
            text_color="grey"
        )

    def update_description_text(self, text, state: bool):
        """
        Выставляем описание по статусу,
        если True - зеленым текстом, False - красным
        """
        color = "red"
        if state:
            color = "green"
        self.version_description_label.configure(
            text=text,
            text_color=color
        )
