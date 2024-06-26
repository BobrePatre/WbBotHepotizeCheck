from aiogram.fsm.state import StatesGroup, State


class BudgetConrol(StatesGroup):
    min_amount = State()
