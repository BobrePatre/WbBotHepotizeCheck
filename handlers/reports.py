import io

import openpyxl
from aiogram import Router, Dispatcher, Bot, types, filters, F
from aiogram.fsm.context import FSMContext

from keyboards.utils import get_url_button
from keyboards.reports import get_report_type_choise
from states.reports import ChooseReportType, ReportTypeExcel


class Reports:
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.router = Router(name="warehouse")

    async def start_choose_report(self, msg: types.Message, state: FSMContext):
        await self.bot.send_message(
            msg.from_user.id,
            "Для начала нужно определится как Вам удобнее работать. "
            "Вы можете заполнить данные по расходам через Excel таблицу,"
            " или внести их через чат с ботом. Что выберем?",
            reply_markup=get_report_type_choise()
        )
        await state.set_state(ChooseReportType.type)

    async def choose_report(self, msg: types.Message, state: FSMContext):
        await self.bot.send_message(
            msg.from_user.id,
            "Пожалуйста, заполните все выделенные ячейки в таблице, после "
            "этого отправьте ее обратно в сообщения. Если Вам проще внести "
            "данные по unit-экономике через сообщения в боте, нажмите на "
            "кнопку назад(появляется кнопка назад, она относит пользователя "
            "на меню с выбором “Excel” и “Чат с ботом”)",
            reply_markup=get_url_button(
                "Таблица",
                "https://docs.google.com/spreadsheets/d/1eioRhpqtvYAVIRU8EL85BmplxR06tfPH/edit?usp=sharing&ouid"
                "=108814234422013602766&rtpof=true&sd=true",
            )
        )
        await state.set_state(ReportTypeExcel.file)

    async def save_file(self, msg: types.Message, state: FSMContext):
        document = msg.document
        if document is None:
            await msg.reply("Пришлите файл с таблицой")
        if document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            file_info = await self.bot.get_file(document.file_id)
            file_path = file_info.file_path
            file = await self.bot.download_file(file_path)
            wb = openpyxl.load_workbook(io.BytesIO(file.read()))
            sheet = wb.active
            data = []
            for row in sheet.iter_rows():
                data.append(row)
            await msg.reply(f"Файл успешно распарсен! Данные файла:\n{data}")
        else:
            await msg.reply("Пожалуйста, пришлите корректный Excel файл.")
            return
        await state.clear()

    # Register Zone
    def register_handlers(self):
        self.router.message.register(self.save_file, filters.StateFilter(ReportTypeExcel.file))
        self.router.callback_query.register(self.choose_report, F.data == "excel")
        self.router.message.register(self.choose_report, F.text == "Отчеты")
        self.dp.include_router(self.router)
