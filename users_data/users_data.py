
# Создаем шаблон заполнения словаря с пользователями
user_templane: dict[str|int|None, str|int] = {
    'user_id': None,
    'user_role': '',
    }


# Инициализируем "базу данных"
users_db : dict[str|int, dict] = {}