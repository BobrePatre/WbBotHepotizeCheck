from aiogram.fsm.state import StatesGroup, State


class UserDataStates(StatesGroup):
    wb_key = State()
