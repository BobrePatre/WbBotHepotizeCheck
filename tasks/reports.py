import asyncio
import logging
from datetime import datetime, timedelta
from io import BytesIO
from aiogram import Bot
from aiogram.types import BufferedInputFile
from openpyxl import Workbook
from gateway.advancements import get_advancement_cost_history
from gateway.marketplace import fetch_orders
from repository.reports import ReportsRepository
from repository.user import UsersRepository


async def generate_report(start_timestamp, end_timestamp, start_date, today, reports_repo, bot, wb_key, user_id):
    reports = reports_repo.get_items_by_user_id(user_id=user_id)
    orders = await fetch_orders(date_from=start_timestamp, date_to=end_timestamp, token=wb_key)

    logging.debug("Fetched orders for user %s: %s", user_id, orders)

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

    advancements = await get_advancement_cost_history(wb_key, from_date=start_date, to_date=today)

    for report in reports:
        order_count = sum(1 for order in orders if order["article"] == report["article"])
        report["profit_excluding_advertising"] = report["unit_profit"] * order_count

        advancement_costs = 0
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

    # Add total values to the table
    sheet.append([])
    sheet.append(
        ["Итого", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", all_advertising_costs, all_profit]
    )

    # Save the file to buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Send the file to the user
    input_file = BufferedInputFile(buffer.read(), filename=f'report_{user_id}_{today}.xlsx')
    await bot.send_document(
        user_id,
        input_file,
        caption=f"Ежедневный отчет в формате excel за {today}\n"
                f"Итого:\n"
                f"Чистая прибыль: {all_profit}\n"
                f"Расходы на рекламу: {all_advertising_costs}",
    )
    logging.info("Report sent to user %s", user_id)
    await asyncio.sleep(60)  # Задержка между запросами для одного пользователя


async def send_report(bot: Bot, user_repository: UsersRepository, reports_repo: ReportsRepository):
    logging.info("Send Report Task Triggered")

    now = datetime.now()
    start_of_previous_day = datetime(now.year, now.month, now.day) - timedelta(days=1)
    end_of_previous_day = start_of_previous_day + timedelta(hours=23, minutes=59, seconds=59)

    start_timestamp = int(start_of_previous_day.timestamp())
    end_timestamp = int(end_of_previous_day.timestamp())

    start_date = start_of_previous_day.strftime('%Y-%m-%d')
    today = now.strftime('%Y-%m-%d')
    users = user_repository.get_all_users()

    logging.info("Fetched all users: %d users found", len(users))

    tasks = []
    for user in users:
        if "wb_key" not in user:
            logging.info("Skipping user without wb_key: %s", user)
            continue

        wb_key = user["wb_key"]
        user_id = user["tg_id"]

        tasks.append(
            generate_report(
                start_timestamp,
                end_timestamp,
                start_date,
                today,
                reports_repo,
                bot,
                wb_key,
                user_id,
            )
        )

    await asyncio.gather(*tasks)

    logging.info("Send Report Task Completed")
