from aiogram.fsm.state import StatesGroup, State


class ChooseReportType(StatesGroup):
    type = State()


class ReportTypeExcel(StatesGroup):
    file = State()
