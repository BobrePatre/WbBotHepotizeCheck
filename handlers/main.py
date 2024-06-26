from aiogram import types, filters
from aiogram import Dispatcher, Router, Bot
from aiogram.fsm.context import FSMContext

from repository.mongo.user import UserRepository

import keyboards.main as kb


class MainHandlers:
    def __init__(self, bot: Bot, dp: Dispatcher, users_repo: UserRepository):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="main_handlers")
        self.users_repo = users_repo

    async def start(self, message: types.Message):
        self.users_repo.create_user(message.from_user.id)
        userdata = self.users_repo.get_user(message.from_user.id)
        print(userdata)
        if "wb_key" not in userdata:
            await self.bot.send_message(
                message.from_user.id,
                "Я бот, который поможет вам рабоать с аналитикой WB 😎",
                reply_markup=kb.get_start_keyboard()
            )
            return
        await self.bot.send_message(message.from_user.id, "Приветик епта!", reply_markup=kb.get_main_keyboard())

    async def unknown(self, message: types.Message):
        await self.bot.send_message(
            message.from_user.id,
            "Я вас не понял 🧐"
        )

    async def error_handler(self, event: types.ErrorEvent):
        print(f'Ошибка бля - {event.exception}')

    def register_handlers(self):
        self.router.error.register(self.error_handler)
        self.router.message.register(self.start, filters.Command("start"))
        self.router.message.register(self.unknown)
        self.dp.include_router(self.router)
