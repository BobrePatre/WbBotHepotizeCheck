from aiogram import Router, filters, types, Dispatcher, Bot, F
from aiogram.fsm.context import FSMContext

import states

router = Router(name="input_user_data")


class InputUserDataHandlers:
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="user_input_handlers")

    async def start_input_user_data(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(message.from_user.id, "🤔Пришлите ваш ключь WB:")
        await state.set_state(state=states.UserDataStates.wb_key)

    async def input_user_data(self, message: types.Message, state: FSMContext):
        await state.set_data({
            "wb_key": message.text
        })
        await self.bot.send_message(message.from_user.id, f"Ваш ключ wb получен! - {message.text}")
        await state.set_state(state=None)

    async def check_wb_key(self, message: types.Message, state: FSMContext):
        userdata = await state.get_data()
        if "wb_key" not in userdata:
            await self.bot.send_message(message.from_user.id, "Мы не нашли ваш api ключ 😭")
        await self.bot.send_message(message.from_user.id, userdata["wb_key"])

    def register_handlers(self):
        self.router.message.register(self.start_input_user_data, F.text == "Начать 👋")
        self.router.message.register(self.input_user_data, filters.StateFilter(states.UserDataStates.wb_key))
        self.router.message.register(self.check_wb_key, filters.Command("check"))
        self.dp.include_router(self.router)
