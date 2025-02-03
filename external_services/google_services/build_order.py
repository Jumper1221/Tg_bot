from datetime import date

from aiogram import Bot
from aiogram.types import Message, CallbackQuery


from .upload_orders import orders_to_publish
from .upload_image_to_drive import get_image_url


# Этот файл будет отвечать за конструирование заказа
# (наполнение необходимыми данными и т.д.)


# Получаем необходимые данные и формируем словарь для заказа
async def build_order(user_order: dict, bot: Bot, message: Message|CallbackQuery):
    new_order = {}
    new_order.update(user_order)
    new_order['order_date'] = date.today().strftime('%d.%m.%Y')
    new_order['draw_link'] = await get_image_url(photo_id = user_order['photo_id'], bot=bot)

    orders_to_publish.append(new_order)
    print(orders_to_publish)
