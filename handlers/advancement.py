from aiogram import Router, Dispatcher, Bot, types, F, filters
from aiogram.fsm.context import FSMContext

from keyboards.advancement import get_advancement_menu
from states.advancement import BudgetConrol
from repository.advancement import AdvancementRepository


class AdvancementHandlers:
    def __init__(self, bot: Bot, dp: Dispatcher, repo: AdvancementRepository):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="advancement")
        self.repo = repo

    async def show_advancement_menu(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(message.from_user.id, "Опции продвижения", reply_markup=get_advancement_menu())

    async def budget_control(self, message: types.Message, state: FSMContext):
        await self.bot.send_message(message.from_user.id,
                                    "Введите минимальный остаток на балансе РК (когда баланс на РК станет меньше этой "
                                    "сумы - бот пришлет Вам уведомление)")
        await state.set_state(BudgetConrol.min_amount)

    async def minimal_amount(self, message: types.Message, state: FSMContext):
        self.repo.set_advancement(message.from_user.id, int(message.text))
        await self.bot.send_message(message.from_user.id,
                                    f"Принял! Теперь когда на балансе ваших РК сумма будет меньше {message.text} - я "
                                    f"вышлю Вам уведомление")
        await state.set_state(None)

    def register_handlers(self):
        self.router.message.register(self.budget_control, F.text == "Контроль бюджета")
        self.router.message.register(self.minimal_amount, filters.StateFilter(BudgetConrol.min_amount))
        self.router.message.register(self.show_advancement_menu, F.text == "Продвижение")
        self.dp.include_router(self.router)
