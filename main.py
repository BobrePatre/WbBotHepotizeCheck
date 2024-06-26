import asyncio
import os

from aiogram import Bot, Dispatcher, types, filters, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from pymongo import MongoClient

from tasks.warehouse import update_stock
from tasks.advancement import check_advancement

# Import repositories
from repository.mongo.user import UserRepository
from repository.mongo.warehouse import WarehouseRepo
from repository.mongo.advancement import AdvancementRepository

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
    mongo_client = MongoClient(os.getenv("MONGO_HOST"), int(os.getenv("MONGO_PORT")))
    app_database = mongo_client.get_database("app")

    # Initialize repositories
    user_repo = UserRepository(app_database)
    warehouse_repo = WarehouseRepo(app_database)
    advancement_repo = AdvancementRepository(app_database)

    # Setup middleware
    dp.message.middleware(AuthMiddleware(user_repo))

    # Register handlers
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
    print("Starting bot...")
    asyncio.run(main())
