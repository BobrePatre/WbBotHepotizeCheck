from aiogram.fsm.state import StatesGroup, State


class AddArticle(StatesGroup):
    article: State = State()
    name: State = State()
    limit: State = State()
    lower_limit: State = State()
    confirm_data: State = State()


class AddProducment(StatesGroup):
    article: State = State()
    productment: State = State()


class ChangingLimit(StatesGroup):
    article: State = State()
    new_limit: State = State()


class ChangingLowerLimit(StatesGroup):
    article: State = State()
    new_limit: State = State()


class ItemsInfo(StatesGroup):
    article: State = State()


class DeleteArticle(StatesGroup):
    article: State = State()