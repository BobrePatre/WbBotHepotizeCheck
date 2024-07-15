import io
import logging

import openpyxl
import openpyxl.worksheet.worksheet
from aiogram import Router, Dispatcher, Bot, types, filters, F
from aiogram.fsm.context import FSMContext

from keyboards.utils import get_url_button
from keyboards.reports import get_report_type_choise
from repository.reports import ReportsRepository
from states.reports import ChooseReportType, ReportTypeExcel


class Reports:
    def __init__(self, bot: Bot, dp: Dispatcher, reports_repo: ReportsRepository):
        self.bot = bot
        self.dp = dp
        self.reports_repo = reports_repo
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
                "https://docs.google.com/spreadsheets/d/e/2PACX-1vT1-xJH2yVYyyMFfzOY"
                "-f6fExCZ_eBvIWJTVZcb7f6INn1GclKJIv-voDH9KFQrzQ/pub?output=xlsx",
            )
        )
        await state.set_state(ReportTypeExcel.file)

    async def save_file(self, msg: types.Message, state: FSMContext):
        document = msg.document
        if document is None:
            await msg.reply("Пришлите файл с таблицей")
            return

        if document.mime_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            await msg.reply("Пожалуйста, пришлите корректный Excel файл.")
            return

        file_info = await self.bot.get_file(document.file_id)
        file_path = file_info.file_path
        file = await self.bot.download_file(file_path)
        wb = openpyxl.load_workbook(io.BytesIO(file.read()))
        sheet = wb.active

        self.reports_repo.clear_items(msg.from_user.id)
        try:
            for row in sheet.iter_rows(min_row=2, values_only=True):
                item = {
                    "article": row[0],
                    "title": row[1],
                    "advancements_ids": str(row[2]).replace(" ", "").split(","),
                    "wb_commission_percents": row[3],
                    "wb_additional_commision_percents": row[4],
                    "purchase_price": row[5],
                    "warehouse_delivery_cost": row[6],
                    "wb_logistics_cost": row[7],
                    "tax_rate": row[8],
                    "packing_cost": row[9],
                    "wb_warehouse_delivery_cost_per_item": row[10],
                    "gift_price": row[11],
                    "defect_percentage": row[12],
                    "other_unit_costs": row[13],
                    "selling_price": row[14],
                }
                if item["article"] is None:
                    continue

                if item["advancements_ids"] == "None":
                    item["advancements_ids"] = []

                if item["other_unit_costs"] is None:
                    item["other_unit_costs"] = 0

                if item["wb_additional_commision_percents"] is None:
                    item["wb_additional_commision_percents"] = 0
                if item["wb_commission_percents"] is None:
                    item["wb_comission_cost"] = (item["selling_price"] / 100 *
                                                 (item["wb_commission_percents"] + item[
                                                     "wb_additional_commision_percents"]))
                else:
                    item["wb_comission_cost"] = (item["selling_price"] / 100 *
                                                 (item["wb_commission_percents"]))
                item["tax_cost"] = (item["selling_price"] / 100) * item["tax_rate"]
                item["defect_costs"] = (item["selling_price"] / 100) * item["defect_percentage"]
                item["cost_price"] = float(item["purchase_price"]) + float(item["warehouse_delivery_cost"]) + float(
                    item[
                        "wb_comission_cost"]) + \
                                     float(item["wb_logistics_cost"]) + float(item["tax_cost"]) + float(
                    item["packing_cost"]) + float(item[
                                                      "wb_warehouse_delivery_cost_per_item"]) + float(item[
                                                                                                          "defect_costs"]) + float(
                    item["other_unit_costs"])
                if item["gift_price"] is not None:
                    item["cost_price"] += float(item["gift_price"])

                item["unit_profit"] = float(item["selling_price"]) - float(item["cost_price"])
                logging.info(item)
                self.reports_repo.add_item(item, msg.from_user.id)
        except Exception as e:
            await msg.reply(
                f"Ошибка при получении данных из таблицы.\nПроверьте таблицу или свяжитесь с поддержкой\nОшибка - {e}")
            logging.exception(e)
        await msg.reply(f"Получил, теперь ежедневно я буду вести учет Ваших продаж\n"
                        "(Бот будет работать с этой таблицей и формировать ежедневные отчеты по прибыли, присылать их "
                        "после окончания дня 00:10 по мск)")
        await state.clear()

    # Register Zone
    def register_handlers(self):
        self.router.message.register(self.save_file, filters.StateFilter(ReportTypeExcel.file))
        self.router.callback_query.register(self.choose_report, F.data == "excel")
        self.router.message.register(self.choose_report, F.text == "Отчеты")
        self.dp.include_router(self.router)
