from Project.settings import RUSSAIN_LOWER


def validate_login_name(char_input):
    """Проверка для ввода логина пользователя"""
    if char_input == "Введите логин" or char_input == "Введите пароль":
        return True

    if len(char_input) > 1:  # правило для инпута больше одного символа
        return all(map(lambda x: x.lower() not in RUSSAIN_LOWER, char_input))

    return char_input != " " and char_input.lower() not in RUSSAIN_LOWER


# функция валидации, которая проверяет, есть ли что-нибудь в Entries, и тогда активирует кнопку
def validate_entries(event=None, button=None, *entries):
    if all(map(lambda x: x.get().strip(), entries)):
        button.configure(state="normal")
    else:
        button.configure(state="disabled")
