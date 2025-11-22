import os
import string
import sys
import random

from datetime import datetime
from pathlib import Path


def resource_path(relative_path):
    """
    Получаем абсолютные пути к файлам в проекте независимо от среды:
    стандартная среда или упакованная через PyInstaller
    """
    try:
        # для PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Стандартное решение
        base_path = os.path.abspath(os.path.dirname(__file__))
    return Path(base_path) / relative_path


def generate_secure_password(allowed_digits, allowed_chars):
    """
    Генерация пароля по правилу:
    -пароль должен содержать минимум 8 символов,
    -хотя бы одну цифру,
    -одну заглавную,
    -одну строчную букву,
    -один специальный символ
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = allowed_digits
    special_chars = allowed_chars

    # Ensure at least one character from each category
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]

    # Fill the rest with random characters from all categories
    remaining_length = random.randint(6, 8)  # Total length will be 10-16 characters
    all_chars = lowercase + uppercase + digits + special_chars
    password.extend(random.choice(all_chars) for _ in range(remaining_length))

    # Shuffle to avoid predictable patterns
    random.shuffle(password)

    # Convert to string
    return ''.join(password)


def str_to_bool(any_input):
    """Превращаем текстовое значение в булево значение"""
    if isinstance(any_input, str):
        return any_input.lower() in ("true", "1", "yes", "t", "y")  # Common truthy strings
    else:
        return bool(any_input)


def int_from_str(any_input):
    """Превращаем текст в число, если возможно"""
    str_is_digit = all(map(lambda x: x.isdigit(), str(any_input)))
    if str_is_digit:
        any_input = int(any_input)
    return any_input


def convert_timestamp(iso_timestamp):
    # Parse the ISO format timestamp into a datetime object
    dt = datetime.fromisoformat(iso_timestamp)
    # Format the datetime object into the desired string format
    formatted_time = dt.strftime('%H:%M:%S %d.%m.%Y')
    return formatted_time


def relative_center(curent_x, current_y, parrent_width, parent_height, width, height):
    """Возвращает координаты для выставления центра"""

    x = curent_x + (parrent_width - width) // 2
    y = current_y + (parent_height - height) // 2
    return x, y
