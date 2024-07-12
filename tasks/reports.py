import logging
import time
from datetime import datetime, timedelta
from io import BytesIO
from aiogram import Bot
from aiogram.types import BufferedInputFile
from openpyxl import Workbook
from gateway.advancements import get_advancement_cost_history
from gateway.marketplace import fetch_orders
from repository.advancement import AdvancementRepository
from repository.reports import ReportsRepository
from repository.user import UsersRepository
from repository.warehouse import WarehouseRepository


async def send_report(
        bot: Bot,
        advancement_repo: AdvancementRepository,
        warehouse_repo: WarehouseRepository,
        user_repository: UsersRepository,
        reports_repo: ReportsRepository,
):
    now = datetime.now()
    start_of_previous_day = datetime(now.year, now.month, now.day) - timedelta(days=1)
    end_of_previous_day = start_of_previous_day + timedelta(hours=23, minutes=59, seconds=59)

    start_timestamp = int(time.mktime(start_of_previous_day.timetuple()))
    end_timestamp = int(time.mktime(end_of_previous_day.timetuple()))

    start_date = datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%d')
    end_date = datetime.fromtimestamp(end_timestamp).strftime('%Y-%m-%d')
    today = datetime.today().strftime('%Y-%m-%d')
    users = user_repository.get_all_users()

    for user in users:
        if "wb_key" not in user:
            continue
        wb_key = user["wb_key"]
        user_id = user["tg_id"]
        reports = reports_repo.get_items_by_user_id(user_id=user_id)
        orders = fetch_orders(
            date_from=start_timestamp,
            date_to=end_timestamp,
            token=wb_key,
        )
        logging.debug(orders)
        all_profit = 0
        all_advertising_costs = 0

        workbook = Workbook()
        sheet = workbook.active
        headers = [
            "Наименование", "Артикул", "Коммисия Wildberries", "Закупочная цена",
            "Доставка до склада", "Логистика wb", "Налоговая ставка", "Сумма налогов",
            "Затраты на упаковку", "Расходы на доставку до склада WB", "Процент брака",
            "Сумма расходов на брак", "Сопутствующие расходы единицу товара",
            "Себестоимость", "Цена продажи", "Заказали штук", "Прибыль за штуку",
            "Прибыль до вычета рекламы", "Затраты на рекламу", "Чистая прибыль"
        ]
        sheet.append(headers)

        for report in reports:
            order_count = sum(1 for order in orders if order["article"] == report["article"])
            report["profit_excluding_advertising"] = report["unit_profit"] * order_count

            advancement_costs = 0
            advancements = get_advancement_cost_history(wb_key, from_date=start_date, to_date=today)
            for advancement_id in report["advancements_ids"]:
                for advancement in advancements:
                    if int(advancement["advertId"]) == int(advancement_id):
                        advancement_costs += advancement["updSum"]

            row = [
                report['title'], report['article'], report['wb_comission_cost'], report['purchase_price'],
                report['warehouse_delivery_cost'], report['wb_logistics_cost'], report['tax_rate'],
                report['tax_cost'], report['packing_cost'], report['wb_warehouse_delivery_cost_per_item'],
                report['defect_percentage'], report['defect_costs'], report['other_unit_costs'],
                report['cost_price'], report['selling_price'], order_count, report['unit_profit'],
                report['profit_excluding_advertising'], advancement_costs,
                report['profit_excluding_advertising'] - advancement_costs
            ]
            sheet.append(row)

            all_profit += report['profit_excluding_advertising'] - advancement_costs
            all_advertising_costs += advancement_costs

        # Добавляем итоговые значения в таблицу
        sheet.append([])
        sheet.append(
            ["Итого", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", all_advertising_costs,
             all_profit])

        # Сохраняем файл в буфер
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Отправляем файл пользователю
        input_file = BufferedInputFile(buffer.read(), filename=f'report_{user_id}_{today}.xlsx')
        await bot.send_document(user_id, input_file, caption=f"Ежедневный отчет в формате excel за {today}\n"
                                                             "Итого:\n"
                                                             f"Чистая прибыль: {all_profit}\n"
                                                             f"Расходы на рекламу: {all_advertising_costs}",)
