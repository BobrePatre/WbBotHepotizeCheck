import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, filters, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from pymongo import MongoClient

from handlers.reports import Reports
from repository.reports import ReportsRepository
from tasks.warehouse import update_stock
from tasks.advancement import check_advancement

# Import repositories
from repository.user import UsersRepository
from repository.warehouse import WarehouseRepository
from repository.advancement import AdvancementRepository

# Import handlers
from handlers.main import MainHandlers
from handlers.input_user_data import InputUserDataHandlers
from handlers.warehouse import Warehouse
from handlers.advancement import AdvancementHandlers

# Import middleware
from middlewares.users import AuthMiddleware

# Import keyboards
import keyboards.main as kb


async def main():
    load_dotenv()

    # Initialize bot and dispatcher
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())

    # Connect to MongoDB
    mongo_uri = f'mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}'
    if os.getenv('DEBUG'):
        mongo_uri = f'mongodb://{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}'

    mongo_client = MongoClient(mongo_uri)
    app_database = mongo_client.get_database("app")

    # Initialize repositories
    reports_repo = ReportsRepository(app_database)
    user_repo = UsersRepository(app_database)
    warehouse_repo = WarehouseRepository(app_database)
    advancement_repo = AdvancementRepository(app_database)
    # Setup middleware
    dp.message.middleware(AuthMiddleware(user_repo))

    # Register handlers
    Reports(bot, dp, reports_repo).register_handlers()
    AdvancementHandlers(bot, dp, advancement_repo).register_handlers()
    Warehouse(bot, dp, warehouse_repo).register_handlers()
    InputUserDataHandlers(bot, dp, user_repo).register_handlers()
    MainHandlers(bot, dp, user_repo).register_handlers()

    # Setup cancel command handler
    @dp.message(filters.Command('cancel'), filters.StateFilter("*"))
    async def cancel(message: types.Message, state: FSMContext):
        await bot.send_message(message.from_user.id, "Действие отменено", reply_markup=kb.get_main_keyboard())
        await state.set_state(None)

    @dp.message(F.text == "На главную", filters.StateFilter("*"))
    async def go_to_main(message: types.Message, state: FSMContext):
        await bot.send_message(message.from_user.id, "Главное меню", reply_markup=kb.get_main_keyboard())
        await state.set_state(None)

    # Start background task
    asyncio.create_task(update_stock(bot, user_repo, warehouse_repo))
    asyncio.create_task(check_advancement(bot, advancement_repo, user_repo))

    # Start polling
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info(f'Starting bot at {os.getenv("BOT_TOKEN")}')
    asyncio.run(main())
