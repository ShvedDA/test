from dataclasses import dataclass
from typing import Callable


@dataclass
class MenuButtonData:
    name: str
    main_text: str
    command: Callable[[], None]

    def add_command(self, func: Callable[[], None]):
        self.command = func

    def get_common_data(self):
        return self.name, self.main_text, self.command


def get_prepared_collection(collection: list['MenuButtonData']):
    """Возвращает кортеж, пригодный для настроек заголовка таблицы"""
    return tuple(map(
        lambda x: x.get_common_data(),
        collection
    ))


# region Описание кнопок
usersButton = MenuButtonData(
    name='usersButton',
    main_text='Пользователи',
    command=None
)

usersHistoryButton = MenuButtonData(
    name='usersHistoryButton',
    main_text="Пользователи\nистория",
    command=None
)

firmwareButton = MenuButtonData(
    name='firmwareButton',
    main_text="Прошивки\n(релиз)",
    command=None
)

firmwareButtonDev = MenuButtonData(
    name='firmwareButtonDev',
    main_text="Прошивки\n(разработка)",
    command=None
)

firmwareHistoryButton = MenuButtonData(
    name='firmwareHistoryButton',
    main_text="Прошивки история\n(релиз)",
    command=None
)

firmwareHistoryButtonDev = MenuButtonData(
    name='firmwareHistoryButtonDev',
    main_text="Прошивки история\n(разработка)",
    command=None
)

devicesButton = MenuButtonData(
    name="devicesButton",
    main_text="Устройства",
    command=None
)

devicesHistoryButton = MenuButtonData(
    name='devicesHistoryButton',
    main_text="Устройства\nистория",
    command=None
)

authButton = MenuButtonData(
    name="authButton",
    main_text="Вход",
    command=None
)

# endregion

buttons_data = (
    usersButton,
    usersHistoryButton,
    firmwareButtonDev,
    firmwareButton,
    firmwareHistoryButtonDev,
    firmwareHistoryButton,
    devicesButton,
    devicesHistoryButton
)
