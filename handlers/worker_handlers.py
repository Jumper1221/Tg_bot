from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from users_data.users_data import users_db
from filters.access_filters import is_worker



router = Router()

router.message.filter(is_worker)

@router.message(F.text == 'тест')
async def process_about(message: Message):
    await message.answer(
        text="Работает!  Теперь ты worker"
        )

# Этот хэндлер будет отлавливать команду /order_list
@router.message(Command(commands='order_list'))
async def process_create_command(message: Message):
    await message.answer('Заглушка для команды планочника <<список заказов>>')

# Этот хэндлер будет отлавливать команду /in_progress
@router.message(Command(commands='in_progress'))
async def process_create_command(message: Message):
    await message.answer('Заглушка для команды планочника <<заказы в производстве>>')

# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help_worker'])