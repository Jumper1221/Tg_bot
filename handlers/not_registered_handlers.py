from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.keyboard_for_not_registered import role_choise_kb
from lexicon.lexicon_ru import LEXICON_RU
from users_data.users_data import user_templane, users_db

from copy import deepcopy
#from services.services import get_bot_choice, get_winner


import logging
# Инициализируем логгер
logger = logging.getLogger(__name__)


def _create_user(message: Message):
    #Если айдишник не Ноне и в базе нет записи с этим айдишником
    if message.from_user is not None and users_db.get(message.from_user.id) is None:
        users_db[message.from_user.id] = deepcopy(user_templane)
        users_db[message.from_user.id]['user_role'] = 'not_registered'
        users_db[message.from_user.id]['user_id'] = message.from_user.id
        logger.info('Creating new user...')
    return True

router = Router()
router.message.filter(_create_user)

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    _create_user(message)
    await message.answer(
        text=LEXICON_RU['/start'] + f"\n\n your role is {users_db[message.from_user.id]['user_role']}",
        reply_markup=role_choise_kb
        )

# Этот хэндлер срабатывает на команду 'о боте'
@router.message(F.text == LEXICON_RU['about'])
async def process_about(message: Message):
    await message.answer(
        text=LEXICON_RU['/help'],
        reply_markup=ReplyKeyboardRemove()
        )

# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Этот хэндлер срабатывает на команду 'менеджер'
@router.message(F.text == LEXICON_RU['manager'])
async def process_about(message: Message):
    users_db[message.from_user.id]['user_role'] = 'manager'
    await message.answer(
        text="Тестируем захват информации:\n\n"
        f'{message.from_user.id} - твой id'
        f"\n{users_db[message.from_user.id]['user_role']} - твоя роль",
        reply_markup=ReplyKeyboardRemove()
        )

# Этот хэндлер будет срабатывать на любые ваши сообщения,
# которые не подходят ни под один обработчик
@router.message()
async def send_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text=LEXICON_RU['no_echo'])