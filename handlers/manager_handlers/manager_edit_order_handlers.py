from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (Message, PhotoSize, CallbackQuery,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           InputMediaPhoto
                           )

from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from handlers.manager_handlers.manager_create_order_handlers import FSM_create_order
from users_data.users_data import users_db
from keyboards.keyboard_for_orders import kb_add_description,kb_apply_order,kb_edit_order
from filters import order_filters



manager_edit_order_router = Router()


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM (рудактирование анкеты)
class FSM_edit_order(StatesGroup):
    editing_order = State()
    edit_1C_number = State()
    edit_desired_date_complete = State()
    edit_drawing = State()
    edit_description = State()

# метод для отображения заказа и клавиатуры с выбором что отредактировать или подтвердить заказ
async def show_order(message: Message, state: FSMContext):
    await state.set_state(FSM_edit_order.editing_order)
    dct = await state.get_data()

    await message.answer_photo(
            photo = dct['photo_id'],
            caption = f'Номер в 1С: {dct["nomer_1C"]}\n'
                      f'Желаемая дата изготовления: {dct["desired_date_complete"]}\n'
                      f'Комментарий: {dct["description"]}\n',
            reply_markup = kb_edit_order
        )


# Если нажали кнопку "редактировать заказ", то переходим к редактированию заказа
@manager_edit_order_router.callback_query(F.data == 'edit_order')
async def process_edit_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSM_edit_order.editing_order)
    dct = await state.get_data()

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=dct['photo_id'],
            caption=f'Номер в 1С: {dct["nomer_1C"]}\n'
                    f'Желаемая дата изготовления: {dct["desired_date_complete"]}\n'
                    f'Комментарий: {dct["description"]}\n'
            ),
    reply_markup=kb_edit_order
    )


# Редактируем номер 1С
@manager_edit_order_router.callback_query(StateFilter(FSM_edit_order.editing_order), F.data == 'edit_order_1C_number')
async def process_edit_1c_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text='Введите номер 1С')
    await state.set_state(FSM_edit_order.edit_1C_number)


# Номер 1С введен корректно
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_1C_number),order_filters.is_correct_1c_number)
async def process_change_1c_number(message: Message, state: FSMContext):
    await state.update_data(nomer_1C=message.text)
    await message.answer(text='Спасибо, данные изменены')
    await show_order(message, state)


# Номер 1С введен некоректно
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_1C_number))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на номмер заказа из 1С\n\n'
             'Пожалуйста, введите номер заказа из 1С\n\n'
             'Если вы хотите прервать создание заказа - '
             'отправьте команду /cancel'
    )


# Редактируем желаемую дату готовности
@manager_edit_order_router.callback_query(StateFilter(FSM_edit_order.editing_order), F.data == 'edit_order_desired_date')
async def process_edit_1c_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text='Введите желаемую дату готовности')
    await state.set_state(FSM_edit_order.edit_desired_date_complete)


# Желаемая дата готовности введена корректно
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_desired_date_complete),
                                    order_filters.is_correct_desired_date)
async def process_change_desired_date(message: Message, state: FSMContext):
    await state.update_data(desired_date_complete=message.text)
    await message.answer(text='Спасибо, данные изменены')
    await show_order(message, state)


# Желаемая дата готовности введена некорректно
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_desired_date_complete))
async def warning_not_desired_date(message: Message, state: FSMContext):
    await message.answer(
            text='То, что вы отправили не похоже на дату\n\n'
                'Пожалуйста, введите желаемую дату готовности заказа\n\n'
                'Если вы хотите прервать создание заказа - '
                'отправьте команду /cancel'
        )


# Редактируем номер изображение чертежа
@manager_edit_order_router.callback_query(StateFilter(FSM_edit_order.editing_order), F.data == 'edit_order_draw')
async def process_edit_drawing(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text='Загрузите изображение чертежа')
    await state.set_state(FSM_edit_order.edit_drawing)


# Отправлено фото чертежа
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_drawing),
                                          order_filters.is_correct_drawing,
                                          F.photo[-1].as_('largest_photo'))
async def process_change_drawing(message: Message, state: FSMContext, largest_photo: PhotoSize):
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
        )
    await message.answer(text='Спасибо, данные изменены')
    await show_order(message, state)


# Отправлено не фото чертежа
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_drawing))
async def warning_not_drawing(message: Message):
    await message.answer(
        text='Пожалуйста, '
             'изображение чертежа\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel'
        )


# Редактируем описание
@manager_edit_order_router.callback_query(StateFilter(FSM_edit_order.editing_order), F.data == 'edit_order_description')
async def process_edit_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text='Напишите описание для заказа')
    await state.set_state(FSM_edit_order.edit_description)


# Описание введено правильно
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_description),order_filters.is_correct_description)
async def process_change_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text='Спасибо, данные изменены')
    await show_order(message, state)


# Описание введено некорректно
@manager_edit_order_router.message(StateFilter(FSM_edit_order.edit_description))
async def warning_not_description(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на описание\n\n'
             'Пожалуйста, введите описание\n\n'
             'Если вы хотите прервать создание заказа - '
             'отправьте команду /cancel'
        )