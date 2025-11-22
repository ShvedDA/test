from dataclasses import dataclass


@dataclass
class UserDataColumn:
    name: str
    header_name: str
    width: int
    anchor: str

    def get_common_columndata(self):
        return self.name, self.header_name, self.width, self.anchor


def get_prepared_collection(collection: list['UserDataColumn']):
    """Возвращает кортеж, пригодный для настроек заголовка таблицы"""
    return tuple(map(
        lambda x: x.get_common_columndata(),
        collection
    ))


id_column = UserDataColumn("id", "ID", 20, 'e')
username_column = UserDataColumn("username", "Имя пользователя", 150, 'center')
role_column = UserDataColumn("role", "Роль", 120, 'center')
statuc_column = UserDataColumn("is_active", "Активен", 120, 'center')

changed_by_column = UserDataColumn("changed_by", "Изменил", 150, "center")
changed_at_column = UserDataColumn("changed_at", "Дата изменения", 200, "center")
changed_field_column = UserDataColumn("changed_field", "Поле", 150, "center")
old_value_column = UserDataColumn("old_value", "Старое значение", 200, "center")
new_value_column = UserDataColumn("new_value", "Новое значение", 200, "center")

version_column = UserDataColumn("version", "Версия", 50, "center")
release_column = UserDataColumn("release_date", "Дата выпуска", 150, "center")
description_column = UserDataColumn("description", "Описание", 300, "center")
info_column = UserDataColumn("info", "Информация", 200, "center")
firmware_status_column = UserDataColumn("is_active", "Статус", 120, 'center')

type_column = UserDataColumn("type", "Тип", 50, 'center')
change_type_column = UserDataColumn("change_type", "Тип", 50, 'center')

itemname_column = UserDataColumn("name", "Название", 150, 'center')
uid_column = UserDataColumn("uid", "UID", 150, 'center')
add_user_column = UserDataColumn("added_by", "Добавил", 80, 'center')
production_column = UserDataColumn("production", "Производство", 100, 'center')
boot_flash_column = UserDataColumn("boot_flash", "Boot Flash", 80, 'center')
app_flash_column = UserDataColumn("app_flash", "App Flash", 80, 'center')
activation_column = UserDataColumn("activation", "Активация", 80, 'center')
creation_date_column = UserDataColumn("creation_date", "Дата создания", 100, 'center')

allUserDataColumns = (
    id_column,
    username_column,
    role_column,
    statuc_column
)

allUserHistoryColumns = (
    id_column,
    changed_by_column,
    changed_at_column,
    changed_field_column,
    old_value_column,
    new_value_column,

)

allDevicesFirmwareColumns = (
    id_column,
    version_column,
    release_column,
    description_column,
    info_column,
    firmware_status_column
)

allFirmwareColumns = (
    id_column,
    type_column,
    version_column,
    release_column,
    description_column,
    info_column,
    firmware_status_column
)

allDevicesDescriptionColumns = (
    id_column,
    itemname_column,
    uid_column,
    add_user_column,
    production_column,
    boot_flash_column,
    app_flash_column,
    activation_column,
    creation_date_column
)

allDevicesHistoryColumns = (
    id_column,
    changed_by_column,
    changed_at_column,
    change_type_column,
    itemname_column,
    uid_column,
    production_column,
    boot_flash_column,
    app_flash_column,
    activation_column
)
