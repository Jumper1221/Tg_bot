from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



# Создаем простую клавиатуру с инлайн кнопками Да/Нет
kb_add_description = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='yes_pressed')],
        [InlineKeyboardButton(text='Нет', callback_data='no_pressed')]
        ]
    )


# Создаем клавиатуру для подтверждения заказа на производство
kb_apply_order = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Подтвердить заказ', callback_data='apply_order')],
        [InlineKeyboardButton(text='Редактировать данные', callback_data='edit_order')]
        ]
    )


# Создаем клавиатуру с выбором: какие данные нужно отредактировать
kb_edit_order = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Изменить номер 1С', callback_data='edit_order_1C_number')],
        [InlineKeyboardButton(text='Изменить желаемую дату готовности', callback_data='edit_order_desired_date')],
        [InlineKeyboardButton(text='Изменить фото чертежа', callback_data='edit_order_draw')],
        [InlineKeyboardButton(text='Изменить описание', callback_data='edit_order_description')],
        [InlineKeyboardButton(text='Подтвердить заказ', callback_data='apply_order')],
        [InlineKeyboardButton(text='Отменить заказ', callback_data='cancel_order')]
        ]
    )