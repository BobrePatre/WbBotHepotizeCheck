import logging
import time
from datetime import datetime, timedelta

from aiogram import Bot

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
    # Текущее время
    now = datetime.now()

    # Начало предыдущего дня (00:00:00)
    start_of_previous_day = datetime(now.year, now.month, now.day) - timedelta(days=1)

    # Конец предыдущего дня (23:59:59)
    end_of_previous_day = start_of_previous_day + timedelta(hours=23, minutes=59, seconds=59)

    # Конвертация в Unix timestamp
    start_timestamp = int(time.mktime(start_of_previous_day.timetuple()))
    end_timestamp = int(time.mktime(end_of_previous_day.timetuple()))

    # Преобразование Unix timestamp обратно в дату с минутами и секундами
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
        for report in reports:

            order_count = 0
            for order in orders:
                if order["article"] == report["article"]:
                    order_count += 1
            report["profit_excluding_advertising"] = report["unit_profit"] * order_count

            advancement_costs = 0
            advancements = get_advancement_cost_history(wb_key, from_date=start_date, to_date=today)
            for advancement_id in report["advancements_ids"]:
                for advancement in advancements:
                    if int(advancement["advertId"]) == int(advancement_id):
                        advancement_costs += advancement["updSum"]

            msg = [
                f"_Данные по товару:_ *{report['title']}*",
                f"Артикул: `{report['article']}`",
                f"Наименование: {report['title']}",
                f"Коммисия Wildberries: {report['wb_comission_cost']}",
                f"Закупочная цена: {report['purchase_price']}",
                f"Доставка до склада: {report['warehouse_delivery_cost']}",
                f"Логистика wb: {report['wb_logistics_cost']}",
                f"Налоговая ставка: {report['tax_rate']}",
                f"Сумма налогов: {report['tax_cost']}",
                f"Затраты на упаковку: {report['packing_cost']}",
                f"Расходы на доставку до склада WB: {report['wb_warehouse_delivery_cost_per_item']}",
                f"Процент брака: {report['defect_percentage']}",
                f"Сумма расходов на брак: {report['defect_costs']}",
                f"Сопутсвующие расходы еденицу товара: {report['other_unit_costs']}",
                f"Себестоимость: {report['cost_price']}",
                f"Цена продажи: {report['selling_price']}",
                f"Заказали штук: {order_count}",
                f"Прибыль за шутку: {report['unit_profit']}",
                f"Прибыль до вычета рекламы: {report['profit_excluding_advertising']}",
                f"Затраты на рекламу: {advancement_costs}",
                f"Чистая прибль: {report['profit_excluding_advertising'] - advancement_costs}",
            ]
            if report["gift_price"] is not None:
                msg.append(f"Цена подарка: {report['gift_price']}")
            all_profit += report['profit_excluding_advertising'] - advancement_costs
            all_advertising_costs += advancement_costs
            await bot.send_message(
                report["user_id"],
                "\n".join(msg),
                parse_mode="Markdown",

            )
        await bot.send_message(
            user_id,
            "Итого:\n"
            f"Чистая прибль: {all_profit}\n"
            f"Расходы на рекламу: {all_advertising_costs}",
            parse_mode="Markdown")
