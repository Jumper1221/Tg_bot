from aiogram.types import Message
from users_data.users_data import users_db




def is_manager(message: Message):
    if users_db.get(message.from_user.id, None) is None:
        return False
    return users_db[message.from_user.id]["user_role"] == 'manager'

def is_worker(message: Message):
    if users_db.get(message.from_user.id, None) is None:
        return False
    return users_db[message.from_user.id]["user_role"] == 'worker'

def is_admin(message: Message):
    if users_db.get(message.from_user.id, None) is None:
        return False
    return users_db[message.from_user.id]["user_role"] == 'admin'