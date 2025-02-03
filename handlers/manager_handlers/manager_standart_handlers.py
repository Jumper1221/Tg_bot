from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (Message, PhotoSize, CallbackQuery,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           InputMediaPhoto
                           )

from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from handlers.manager_handlers.manager_create_order_handlers import manager_order_router
from handlers.manager_handlers.manager_edit_order_handlers import manager_edit_order_router
from lexicon.lexicon_ru import LEXICON_RU
from users_data.users_data import users_db
from filters.access_filters import is_manager
from keyboards.keyboard_for_orders import kb_add_description,kb_apply_order,kb_edit_order



router = Router()
# переделать и вынести фильтр в отдельный файл и назвать его is_manager
router.message.filter(is_manager)
router.include_router(manager_order_router)
router.include_router(manager_edit_order_router)


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний\n\n'
             'Чтобы перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )


@router.message(F.text == 'тест')
async def process_about(message: Message):
    await message.answer(
        text="Работает!  Теперь ты менеджер"
        )


# Этот хэндлер будет отлавливать команду /order_list
@router.message(Command(commands='order_list'))
async def process_create_command(message: Message):
    await message.answer('Заглушка для команды менеджера <<список заказов>>')

# Этот хэндлер будет отлавливать команду /in_progress
@router.message(Command(commands='in_progress'))
async def process_create_command(message: Message):
    await message.answer('Заглушка для команды менеджера <<заказы в производстве>>')


# Этот хэндлер будет отлавливать команду /create
@router.message(Command(commands='create'))
async def process_create_command(message: Message):
    await message.answer('Заглушка для команды менеджера <<создать>>')

# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help_manager'])