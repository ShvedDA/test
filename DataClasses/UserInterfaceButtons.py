from dataclasses import dataclass
from typing import Callable


@dataclass
class UserInterfaceButtons:
    name: str
    main_text: str
    state: str
    command: Callable[[], None]

    def add_command(self, func: Callable[[], None]):
        self.command = func

    def get_common_columndata(self):
        return self.name, self.main_text, self.state, self.command


def get_prepared_collection(collection: list['UserInterfaceButtons']):
    """Возвращает кортеж, пригодный для настроек заголовка таблицы"""
    return tuple(map(
        lambda x: x.get_common_columndata(),
        collection
    ))


reloadButton = UserInterfaceButtons(
    name='reloadButton',
    main_text='Обновить',
    state='normal',
    command=None  # command=self.load_users
)
addUsersButton = UserInterfaceButtons(
    name='addUsersButton',
    main_text='Создать',
    state='normal',
    command=None  # command=self.add_user
)
editUsersButton = UserInterfaceButtons(
    name='editUsersButton',
    main_text='Изменить',
    state='disabled',
    command=None  # command=self.edit_user
)
blockUsersButton = UserInterfaceButtons(
    name='blockUsersButton',
    main_text='Заблокировать',
    state='disabled',
    command=None  # , command=self.block_user,
)
unblockUsersButton = UserInterfaceButtons(
    name='unblockUsersButton',
    main_text='Активировать',
    state='disabled',
    command=None  # , command=self.unlock_user,
)

reloadDeviceButton = UserInterfaceButtons(
    name='reloadButton',
    main_text='Обновить',
    state='normal',
    command=None  # command=self.load_users
)

addDeviceButton = UserInterfaceButtons(
    name='addDeviceButton',
    main_text='Создать',
    state='normal',
    command=None
)

editDeviceButton = UserInterfaceButtons(
    name='editDeviceButton',
    main_text='Изменить',
    state='normal',
    command=None
)
removeDeviceButton = UserInterfaceButtons(
    name='removeDeviceButton',
    main_text='Удалить',
    state='normal',
    command=None
)

allUserButtons = (
    reloadButton,
    addUsersButton,
    editUsersButton,
    blockUsersButton,
    unblockUsersButton
)

allFirmwareButtons = (
    reloadButton,
    addUsersButton,
    editUsersButton
)

allDevicesButtons = (
    reloadDeviceButton,
    addDeviceButton,
    editDeviceButton,
    removeDeviceButton
)
