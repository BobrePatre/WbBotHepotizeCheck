from aiogram import Router, filters, types, Dispatcher, Bot, F
from aiogram.fsm.context import FSMContext

import keyboards.main

from states.main import UserDataStates

from repository.mongo.user import UserRepository
import keyboards.main as kb

router = Router(name="input_user_data")


class InputUserDataHandlers:
    def __init__(self, bot: Bot, dp: Dispatcher, user_repo: UserRepository):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="user_input_handlers")
        self.user_repo = user_repo

    async def start_input_user_data(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(message.from_user.id, "🤔Пришлите ваш ключь WB:")
        await state.set_state(state=UserDataStates.wb_key)

    async def input_user_data(self, message: types.Message, state: FSMContext):
        await state.set_data({
            "wb_key": message.text
        })
        self.user_repo.save_wb_key(message.from_user.id, message.text)
        await self.bot.send_message(
            message.from_user.id,
            f"Ваш ключ wb получен! - {message.text}",
            reply_markup=kb.get_main_keyboard()
        )
        await state.set_state(state=None)

    def register_handlers(self):
        self.router.message.register(self.start_input_user_data, F.text == "Начать 👋")
        self.router.message.register(self.input_user_data, filters.StateFilter(UserDataStates.wb_key))
        self.dp.include_router(self.router)
