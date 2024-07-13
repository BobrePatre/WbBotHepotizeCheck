
import logging
from datetime import datetime, timedelta
from aiogram import Bot

from gateway.warehouse import get_orders
from repository.user import UsersRepository
from repository.warehouse import WarehouseRepository


async def update_stock(bot: Bot, users_repo: UsersRepository, warehouse_repo: WarehouseRepository):
    logging.info("Update Stock Task Triggered")
    now_moscow = datetime.now()
    date_from = int((now_moscow - timedelta(minutes=10)).timestamp())
    users = users_repo.get_all_users()
    for user in users:
        if "wb_key" not in user:
            continue
        new_orders = get_orders(user["wb_key"], date_from)
        if "orders" not in new_orders:
            return
        new_orders = new_orders["orders"]
        logging.info("Getting new orders %s", new_orders)
        for order in new_orders:
            logging.info(order)
            res = warehouse_repo.get_article(order["article"])
            if res is None:
                continue
            warehouse_repo.set_new_limit(order["article"], int(res["article"]["limit"]) - 1)
            if res["article"]["limit"] - 1 <= res["article"]["lower_limit"]:
                await bot.send_message(res["user_id"],
                                       f"У вас заканчивается {res['article']['name']}! Осталось штук - "
                                       f"{res['article']['limit'] - 1}\n"
                                       f"Ваш нижний порог - {res['article']['lower_limit']}\n")
            print("Лимит уменьшен")
