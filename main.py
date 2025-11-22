import json
import logging
import subprocess
from threading import Thread

from Project.AppFrames.MainUserFrames.DeviceFrame import DeviceFrame
from Project.AppFrames.MainUserFrames.DevicesHistoryFrame import DeviceHistoryFrame
from Project.AppFrames.MainUserFrames.FirmwareFrameRelease import FirmwareFrameRelease
from Project.AppFrames.MainUserFrames.FirmwareFrameDevelop import FirmwareFrameDevelop
from Project.AppFrames.MainUserFrames.FirmwareHistoryFrame import FirmwareHistoryFrame
from Project.AppFrames.LoginFrame import LoginFrame
from Project.AppFrames.MainUserFrames.UserFrame import UserFrame
from Project.AppFrames.MainUserFrames.UserHistoryFrame import UserHistoryFrame
from Project.Commands.ButtonCommand import show_window
from Project.CustomUiParts.MainWindow import StandardApp
from Project.DataClasses.AppUser import AppUser
from Project.Services.FrameProperties import disable_frame, enable_frame
from Project.AppFrames.MainMenuFrame import MainMenu
from Project.api_manager import APIManager


CUR_VERSION = "v1_1_6"


class App(StandardApp):
    def change_auth_button(self, state: bool):
        """
        Метод смены логики и текста кнопки аутентификации,
        где state = False, логаут пользователя, True - log in
        """
        auth_button = self.menuFrame.get_button("authButton")
        button_text = "Войти"
        button_command = None
        if not state:
            button_text = "Выйти"
            button_command = self.logout_button_click
        auth_button.configure(text=button_text, command=button_command)

    def login_button_click(self):
        """Событие, при клике на кнопку "Войти" во фрейме авторизации"""
        self.authFrame.disable_button()
        # меняем текст на анимацию загрузки
        self.authFrame.change_login_status(self.get_theme_gif())
        # обновляем UI вручную
        self.update_idletasks()

        username, password = self.authFrame.read_userinput()

        def perform_login():
            try:
                error_message = self.api_manager.login(username, password)
                # убираем гифку загрузки
                self.authFrame.remove_gif()
                if error_message is None:  # всё ок
                    # выставляем пользователя
                    self.User.set_data(username)
                    # обновляем название окна
                    self.title(self.title() + f" - {self.User.login_name}")
                    # обновляем UI
                    self.after(0, lambda frame=self.menuFrame: enable_frame(self.menuFrame))
                    self.after(0, self.user_button_click())
                    self.after(0, lambda: self.change_auth_button(False))
                    self.after(0, self.authFrame.clean_user_input())
                    self.after(0, self.authFrame.complete_cleanup())
                    self.after(0, self.authFrame.change_login_status())
                    self.after(0, self.authFrame.update())
                else:
                    self.after(0, self.authFrame.update())
                    # проверяем известные ошибки
                    if error_message == "Incorrect username or password":
                        self.after(0, lambda: self.authFrame.change_login_status(
                            "Неверный логин или пароль", False))
                    else:
                        self.after(0, lambda error=error_message: self.authFrame.change_login_status(error, False))
            except subprocess.CalledProcessError as e:
                self.after(0, self.authFrame.change_login_status("Ошибка подключения к сети", False))
                logger.error(f"Ошибка curl при логине: {e.stderr}")
            except json.JSONDecodeError:
                self.after(0, self.authFrame.change_login_status("Ошибка на сервере", False))
                logger.error("Ошибка декодирования JSON ответа сервера")
            except Exception as e:
                self.after(0, self.authFrame.change_login_status("Неизвестная ошибка системы", False))
                logger.error(f"Непредвиденная ошибка при логине: {e}")
            finally:
                # обновляем UI в любой ситуации
                self.after(0, self.authFrame.remove_gif())
                self.after(0, self.authFrame.complete_cleanup())

        # Выполняем запрос на другом потоке, чтобы избежать заморозки UI
        Thread(target=perform_login, daemon=True).start()

    def logout_button_click(self):
        """Событие, при клике на кнопку "Выйти" в меню"""

        def handle_logout_continuation():
            """Функция, которая выполнится только после ответа block_while_active_threads"""
            # Обновляем название основного окна
            updated_title = " - ".join(self.title().split(" - ")[:-1])
            self.title(updated_title)

            # Обновляем UI
            self.change_auth_button(True)
            show_window("authButton", self.frames_dict, self.menuFrame.get_button_list())
            disable_frame(self.menuFrame)
            self.api_manager.clean_api_manager()
            self.User.logout_user()

        # Start thread check with callback
        self.block_while_active_threads(on_complete=handle_logout_continuation)

    def user_button_click(self):
        """Событие при нажатии на кнопку пользователей"""
        show_window("usersButton", self.frames_dict, self.menuFrame.get_button_list())
        self.userFrame.reload_users()

    def userhistory_button_click(self):
        """
        Обновляем состав пользователей в таблице.
        """
        show_window("usersHistoryButton", self.frames_dict, self.menuFrame.get_button_list())

        self.async_update_table(
            data_func=self.api_manager.get_all_users,
            headers=self.userHistoryFrame.headers,
            update_func=self.userHistoryFrame.userTableFrame.update_data,
            callback=self.userHistoryFrame.userTableFrame.bootTableFrame.scroll_to_last_item)

    def firmware_button_click(self):
        """
        Получаем информацию о всех прошифках по клику
        """
        show_window("firmwareButton", self.frames_dict, self.menuFrame.get_button_list())

        # обновляем таблицы
        self.firmwareFrame.async_reload_data()

    def firmware_dev_button_click(self):
        """
        Получаем информацию о всех прошифках по клику
        """
        show_window("firmwareButtonDev", self.frames_dict, self.menuFrame.get_button_list())

        # обновляем таблицы
        self.firmwareFrameDev.async_reload_data()

    def firmware_history_button_click(self):
        """
        Получаем информацию о всех прошифках по клику
        """
        show_window("firmwareHistoryButton", self.frames_dict, self.menuFrame.get_button_list())

        self.async_update_table(
            data_func=lambda: self.api_manager.get_all_firmwaredata(False),
            headers=self.firmwareHistoryFrame.headers,
            update_func=self.firmwareHistoryFrame.firmwareTableFrame.update_data,
            callback=self.firmwareHistoryFrame.firmwareTableFrame.bootTableFrame.scroll_to_last_item)

    def firmware_history_dev_button_click(self):
        """
        Получаем информацию о всех прошифках по клику
        """
        show_window("firmwareHistoryButtonDev", self.frames_dict, self.menuFrame.get_button_list())

        self.async_update_table(
            data_func=lambda: self.api_manager.get_all_firmwaredata(True),
            headers=self.firmwareHistoryFrameDev.headers,
            update_func=self.firmwareHistoryFrameDev.firmwareTableFrame.update_data,
            callback=self.firmwareHistoryFrameDev.firmwareTableFrame.bootTableFrame.scroll_to_last_item)

    def device_button_click(self):
        """Событие при нажатии на кнопку 'Устройства'"""
        self.deviceFrame.filter_text_input.clean()  # чистим поле перед запуском фрейма
        show_window("devicesButton", self.frames_dict, self.menuFrame.get_button_list())
        self.deviceFrame.async_reload_data()

    def device_history_button_click(self):
        """
        Получаем информацию о всех прошифках по клику
        """
        self.deviceHistoryFrame.filter_text_input.clean()  # чистим поле перед запуском фрейма
        show_window("devicesHistoryButton", self.frames_dict, self.menuFrame.get_button_list())
        self.deviceHistoryFrame.async_reload_data()

    def __init__(self, app_name: str, *args, **kwargs):
        super().__init__(app_name, *args, **kwargs)

        self.api_manager = APIManager()
        self.grid_columnconfigure(0, minsize=150, uniform="cols")
        self.grid_columnconfigure(1, weight=5, uniform="cols")
        self.rowconfigure(0, weight=1)

        # Пользователь
        self.User = AppUser(self)

        # кнопки меню
        self.menuFrame = MainMenu(self)
        self.menuFrame.grid(row=0, column=0, padx=(6, 3), pady=5, sticky="NSEW")

        # region ОБЪЯВЛЕНИЕ ОКОН ПОЛЬЗОВАТЕЛЯ
        self.authFrame = LoginFrame(self)  # окно авторизации
        self.authFrame.grid(row=0, column=1, padx=(3, 6), pady=5, sticky="NSEW")
        self.userFrame = UserFrame(self)  # окно пользователя
        self.userHistoryFrame = UserHistoryFrame(self)  # окно действия пользователей
        self.firmwareFrame = FirmwareFrameRelease(self)  # окно по работе с прошивками (релиз)
        self.firmwareFrameDev = FirmwareFrameDevelop(self)  # окно по работе с прошивками (разработка)
        self.firmwareHistoryFrame = FirmwareHistoryFrame(self, dev_mode=False)  # окно логирования действий с прошивками (релиз)
        self.firmwareHistoryFrameDev = FirmwareHistoryFrame(self, dev_mode=True)  # окно логирования действий с прошивками (разработка)
        self.deviceFrame = DeviceFrame(self)  # окно по работе с устройствами
        self.deviceHistoryFrame = DeviceHistoryFrame(self)  # окно логирования действий с устройствами
        # endregion

        # Словарь для мэпинга кнопок и окон
        self.frames_dict = {
            "usersButton": self.userFrame,
            "usersHistoryButton": self.userHistoryFrame,
            "firmwareButton": self.firmwareFrame,
            "firmwareButtonDev": self.firmwareFrameDev,
            "firmwareHistoryButton": self.firmwareHistoryFrame,
            "firmwareHistoryButtonDev": self.firmwareHistoryFrameDev,
            "devicesButton": self.deviceFrame,
            "devicesHistoryButton": self.deviceHistoryFrame,
            "authButton": self.authFrame,
        }

        # замораживаем фрейм
        disable_frame(self.menuFrame)

        # биндим кнопки внутри фреймов
        self.authFrame.add_command_to_frame(self.login_button_click)
        self.menuFrame.add_command_to_button("usersButton", self.user_button_click)
        self.menuFrame.add_command_to_button("usersHistoryButton", self.userhistory_button_click)
        self.menuFrame.add_command_to_button("firmwareButton", self.firmware_button_click)
        self.menuFrame.add_command_to_button("firmwareButtonDev", self.firmware_dev_button_click)
        self.menuFrame.add_command_to_button("firmwareHistoryButton", self.firmware_history_button_click)
        self.menuFrame.add_command_to_button("firmwareHistoryButtonDev", self.firmware_history_dev_button_click)
        self.menuFrame.add_command_to_button("devicesButton", self.device_button_click)
        self.menuFrame.add_command_to_button("devicesHistoryButton", self.device_history_button_click)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    app = App("Менеджер БД")
    app.mainloop()
