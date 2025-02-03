from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU

# Создаем кнопки с ответами согласия и отказа
button_manager_register = KeyboardButton(text=LEXICON_RU['manager'])
button_worker_register = KeyboardButton(text=LEXICON_RU['worker'])
button_admin_register = KeyboardButton(text=LEXICON_RU['admin'])
button_about = KeyboardButton(text=LEXICON_RU['about'])

# Инициализируем билдер для клавиатуры с кнопками "Давай" и "Не хочу!"
role_kb_builder = ReplyKeyboardBuilder()

# Добавляем кнопки в билдер с аргументом width=2
role_kb_builder.row(
    button_manager_register,
    button_worker_register,
    button_admin_register,
    button_about,
    width=1
    )

# Создаем клавиатуру с кнопками
role_choise_kb: ReplyKeyboardMarkup = role_kb_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)
