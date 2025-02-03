from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (Message, PhotoSize, CallbackQuery,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           InputMediaPhoto
                           )

from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from users_data.users_data import users_db
from keyboards.keyboard_for_orders import kb_add_description,kb_apply_order,kb_edit_order

from external_services.google_services.build_order import build_order



manager_order_router = Router()


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM (анкета)
class FSM_create_order(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_1C_number = State()                     # Состояние ожидания ввода номера заказа
    fill_desired_date_complete = State()         # Состояние ожидания ввода желаемой даты изготовления
    upload_drawing = State()                     # Состояние ожидания загрузки чертежа
    fill_description = State()                   # Состояние ожидания ввода описания



# Создаем временную базу данных для теста в виде словаря
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@manager_order_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из машины состояний\n\n'
             'Чтобы снова перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода номер заказа в 1С
@manager_order_router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите номер заказа в 1С')
    # Устанавливаем состояние ожидания ввода номер заказа в 1С
    await state.set_state(FSM_create_order.fill_1C_number)


# Этот хэндлер будет срабатывать, если введен корректный номер
# и переводить в состояние ожидания ввода желаемой даты готовности
@manager_order_router.message(StateFilter(FSM_create_order.fill_1C_number), F.text.isdigit(), F.text.len() < 5)
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(nomer_1C=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите желаемую дату готовности заказа')
    # Устанавливаем состояние ожидания ввода желаемой даты готовности заказа
    await state.set_state(FSM_create_order.fill_desired_date_complete)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@manager_order_router.message(StateFilter(FSM_create_order.fill_1C_number))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на номмер заказа из 1С\n\n'
             'Пожалуйста, введите номер заказа из 1С\n\n'
             'Если вы хотите прервать создание заказа - '
             'отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать, если введена корректно желаемая дата готовности заказа
# С помощью регулярки ищем дату формата 00.00 и отсекаем 30 и 31 февраля (с 29-м не заморачивался)
# Еще косяк с месяцами, в которых 30 дней, нужно будет найти более изящное решение
@manager_order_router.message(StateFilter(FSM_create_order.fill_desired_date_complete),
                F.text.regexp(r"^((0?[1-9])|([12]\d)|(3[01]))[.:-]((0?[1-9])|(1[12]))$"),
                ~F.text.regexp(r"^(3[01])[.:-](0?2)$")
                )
async def process_fill_desired_date(message: Message, state: FSMContext):
    await state.update_data(desired_date_complete=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите, пожалуйста, изображение чертежа')
    # Устанавливаем состояние ожидания картинки с чертежом
    await state.set_state(FSM_create_order.upload_drawing)


# Этот хэндлер будет срабатывать, если ввели некорректно желаемую дату готовности заказа
@manager_order_router.message(StateFilter(FSM_create_order.fill_desired_date_complete))
async def warning_not_desired_date(message: Message, state: FSMContext):
    await message.answer(
        text='То, что вы отправили не похоже на дату\n\n'
             'Пожалуйста, введите желаемую дату готовности заказа\n\n'
             'Если вы хотите прервать создание заказа - '
             'отправьте команду /cancel'
    )


#Этот хендлер сработает, если мы отправили фото
@manager_order_router.message(StateFilter(FSM_create_order.upload_drawing),
                F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message, state: FSMContext, largest_photo: PhotoSize):
    # Cохраняем данные фото (file_unique_id и file_id) в хранилище
    # по ключам "photo_unique_id" и "photo_id"
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
        )

    await message.answer(
    text='Спасибо!\n\n Хотите добавить описание к заказу?',
    reply_markup=kb_add_description
    )

    # Устанавливаем состояние ожидания выбора образования
    #await state.set_state(FSM_create_order.fill_description)


# Этот хэндлер будет срабатывать, если во время отправки чертежа
# будет введено/отправлено что-то некорректное
@manager_order_router.message(StateFilter(FSM_create_order.upload_drawing))
async def warning_not_photo(message: Message):
    await message.answer(
        text='Пожалуйста, на этом шаге отправьте '
             'изображение чертежа\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


#Отлавливаем нажатие на инлайн кнопку ДА
@manager_order_router.callback_query(StateFilter(FSM_create_order.upload_drawing), F.data == 'yes_pressed')
async def process_button_yes_pressed(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Отлично! Добавьте описание к заказу',
        #reply_markup=callback.message.reply_markup
        )
    await state.set_state(FSM_create_order.fill_description)


#Отлавливаем нажатие на инлайн кнопку Нет
@manager_order_router.callback_query(StateFilter(FSM_create_order.upload_drawing), F.data == 'no_pressed')
async def process_button_no_pressed(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description='-')
    await callback.message.edit_text(text='Спасибо!\n\nВсе необходимые данные заполнены!')
    dct = await state.get_data()
    await callback.message.answer_photo(
            photo=dct['photo_id'],
            caption=f'Номер в 1С: {dct["nomer_1C"]}\n'
                    f'Желаемая дата изготовления: {dct["desired_date_complete"]}\n'
                    f'Комментарий: {dct["description"]}\n'
                    f'\n\n<b>Всё верно?</b>',
            reply_markup=kb_apply_order
            )



# Этот хэндлер будет срабатывать, если ввели корректно описание
@manager_order_router.message(StateFilter(FSM_create_order.fill_description), F.text.isalpha())
async def process_fill_desired_date(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(text='Спасибо!\n\nВсе необходимые данные заполнены!')
    dct = await state.get_data()
    await message.answer_photo(
            photo=dct['photo_id'],
            caption=f'Номер в 1С: {dct["nomer_1C"]}\n'
                    f'Желаемая дата изготовления: {dct["desired_date_complete"]}\n'
                    f'Комментарий: {dct["description"]}\n'
                    f'\n\n<b>Всё верно?</b>',
            reply_markup=kb_apply_order
            )


# Этот хэндлер будет срабатывать, если ввели некорректно описание
@manager_order_router.message(StateFilter(FSM_create_order.fill_description))
async def process_fill_desired_date(message: Message, state: FSMContext):
    await message.answer(
        text='То, что вы отправили не похоже на описание\n\n'
             'Пожалуйста, введите описание\n\n'
             'Если вы хотите прервать создание заказа - '
             'отправьте команду /cancel'
    )


# Если нажимаем кнопку подтвердить заказ, сохраняем данные в нашу БД у выходим из машины состояний
@manager_order_router.callback_query(F.data == 'apply_order')
async def process_apply_order(callback: CallbackQuery, state: FSMContext, bot: Bot):

    # убираем клавиатуру с сообщения
    await callback.message.delete_reply_markup()

    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя

    new_order = await state.get_data()
    await build_order(new_order, bot, callback)
    # Завершаем машину состояний
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    await callback.message.answer(
        text='Спасибо! Ваши данные сохранены!\n\n'
             'Вы вышли из машины состояний'
    )








# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@manager_order_router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Номер в 1С: {user_dict[message.from_user.id]["nomer_1C"]}\n'
                    f'Желаемая дата изготовления: {user_dict[message.from_user.id]["desired_date_complete"]}\n'
                    f'Комментарий: {user_dict[message.from_user.id]["description"]}\n'
            )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text='Вы еще не создали заказ. Чтобы приступить - '
            'отправьте команду /fillform'
        )
