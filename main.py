import asyncio

import aiogram
from aiogram import Dispatcher, Router, Bot
from aiogram import types, filters
from aiogram.fsm.storage.memory import MemoryStorage

from input_user_data import InputUserDataHandlers

import kb


class MainHandlers:
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="main_handlers")

    async def start(self, message: types.Message):
        await self.bot.send_message(
            message.from_user.id,
            "Я бот, который поможет вам рабоать с аналитикой WB 😎",
            reply_markup=kb.get_main_keyboard()
        )

    async def unknown(self, message: types.Message):
        await self.bot.send_message(
            message.from_user.id,
            "Я вас не понял 🧐"
        )

    def register_handlers(self):
        self.router.message.register(self.start, filters.Command("start"))
        self.router.message.register(self.unknown)
        self.dp.include_router(self.router)


async def main():
    bot = aiogram.Bot(token='6347391792:AAFYo0FJVXyo2YNT1mCtqMgjlHEH5aHcgic')
    dp = Dispatcher(storage=MemoryStorage())
    InputUserDataHandlers(bot, dp).register_handlers()
    MainHandlers(bot, dp).register_handlers()
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("starting bot...")
    asyncio.run(main())
