import os
from pathlib import Path

from Project.utils import resource_path

# Глобальные настройки файла

# директории
BASE_DIR = resource_path(os.path.dirname(__file__))
IMAGES_DIR = Path("images")

# цветовая палитра
RED_BG_COLOR = "#ae1a1a"  # задний фон элементов
BLUE_ELEMENT_COLOR = "#1f6aa4"  # цвет элементов
DISABLE_COLOR = "#DBBBBB"  # цвет отключенных элементов
DISABLE_TEXT_COLOR = "#BDBDBD"  # цвет отключенных текстовых элементов
ALLOW_COLOR = "#6b8e23"  # цвет, если положительный ответ или успех
BLOCK_COLOR = "red"  # цвет, если отрицательный ответ или провал
TABLE_LIGHT_COLOR = "#F0F0F0"  # задний фон таблицы для светлой темы
TEXT_LIGHT_TABLE_COLOR = "#404040"  # текст таблицы для светлой темы
TABLE_DARK_COLOR = "#2a2d2e"  # задний фон таблицы для темной темы
TEXT_DARK_TABLE_COLOR = "white"  # текст таблицы для темной темы

# шрифты
FONT_ADDITIONAL = ("Segoe UI", 12)  # шрифт текста пояснений
FONT_ELEMENTS = ("Segoe UI", 14)  # шрифт элементов
FONT_MENU = ("Segoe UI", 16)  # шрифт в меню
FONT_DEFAULT_EDIT_TEXT = ("Segoe UI", 14, 'italic')  # шрифт для текста по умолчанию в текст-боксах

# Параметры окна приложения
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MINSIZE_WINDOW_WIDTH = 1000
MINSIZE_WINDOW_HEIGHT = 600

# Параметры вспомогательных окон
SMALL_WINDOW_WIDTH = 400
SMALL_WINDOW_HEIGHT = 300

# ИНФОРМАЦИЯ С СЕРВЕРА
USERS_ROLES = ["admin", "worker", "user"]  # Возможные роли пользователей в проекте
FIRMWARE_TYPES = {
    "firmware_boot": "Загрузчик",
    "firmware_pst": "PST-контроллер",
    "firmware_pos": "Позиционер"
}  # Типы прошивок

# допустимые варианты прошивок (релиз версия)
POSSIBLE_FIRMWARE_TYPES_REL = {
    "Загрузчик": ["firmware_boot"],
    "PST-контроллер": ["firmware_pst"],
    "Позиционер": ["firmware_pos"],
    "PST-контроллер и позиционер": ["firmware_pst", "firmware_pos"]
}

# допустимые варианты прошивок (девелоп версия)
POSSIBLE_FIRMWARE_TYPES_DEV = {
    "PST-контроллер": ["firmware_pst"],
    "Позиционер": ["firmware_pos"],
    "PST-контроллер и позиционер": ["firmware_pst", "firmware_pos"]
}


# гифки
LOADING_STANDARD_GIF = IMAGES_DIR / "loading_light.gif"  # путь к стандартной гифке
DARK_LOADING_GIF = IMAGES_DIR / "loading_dark.gif"  # путь к гифке для темной темы

# Некоторые фразы
SETUP_PASSWORD = "Пароль должен содержать минимум 8 символов,\nхотя бы одну цифру, одну заглавную и строчную букву,\nи один специальный символ."
READY_PASSWORD = "Пароль соответсвует требованиям!"

# ИСХОДНЫЕ СИМВОЛЫ ДЛЯ ГЕНЕРАЦИИ ПАРОЛЯ
PASSWORD_DIGITS = "0123456789"
PASSWORD_SPECIAL_CHARS = '!#$%^&*_?'

RUSSAIN_LOWER = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
