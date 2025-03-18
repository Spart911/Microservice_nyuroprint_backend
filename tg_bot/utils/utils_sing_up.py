import re

# Функция для проверки корректности email
def is_valid_email(email: str) -> bool:
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return bool(re.match(email_regex, email))

# Функция для проверки пароля (минимум 6 символов, хотя бы одна цифра или буква)
def is_valid_password(password: str) -> bool:
    if len(password) < 6:
        return False
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False
    return True