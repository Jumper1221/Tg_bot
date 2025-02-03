import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.main_menu import set_menu
from config_data.config import Config, load_config
from handlers import other_handlers, not_registered_handlers, admin_handlers, worker_handlers
from handlers.manager_handlers import manager_standart_handlers

from external_services.google_services.upload_orders import check_new_orders



# Импортируем миддлвари
# ...
# Импортируем вспомогательные функции для создания нужных объектов
# ...
# from keyboards.main_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем объект хранилища
    storage = MemoryStorage()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    #dp = Dispatcher(storage=storage)
    dp = Dispatcher(storage=storage)

    # Инициализируем другие объекты (пул соединений с БД, кеш и т.п.)
    # ...

    # Помещаем нужные объекты в workflow_data диспетчера
    # dp.workflow_data.update(...)

    # Настраиваем главное меню бота
    await set_menu(bot)

    logger.info('Подключаем роутеры')

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(worker_handlers.router)
    dp.include_router(manager_standart_handlers.router)
    dp.include_router(not_registered_handlers.router)
    #dp.include_router(other_handlers.router)

    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')
    # ...


    # Запускаем мониторинг новых заказов на отправку
    order_task = asyncio.create_task(check_new_orders())


    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())