# Главный файл, его будем импортировать в main
# и в нем будут находиться все функции
# для проверки и загрузки заказа в гугл таблицу

import asyncio
import logging

from .orders_to_sheet import add_orders_to_sheet

SECOND_TO_WAIT = 30


logger = logging.getLogger(__name__)


# Список, куда будут поступать словари с новыми заказами
orders_to_publish: list[dict] = []


# Проверяет, есть ли новые заказы в очереди на размещение
async def check_new_orders() -> bool:
    while True:
        await asyncio.sleep(SECOND_TO_WAIT)
        logger.info('Сработала проверка на новые заказы')
        if orders_to_publish:
            if add_orders_to_sheet(orders_to_publish):
                orders_to_publish.clear()
            else:
                raise Exception('Косяк с записью двнных в таблицу')
