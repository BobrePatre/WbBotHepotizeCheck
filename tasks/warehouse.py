import asyncio
from datetime import datetime, timedelta
from aiogram import Bot

from gateway.warehouse import get_orders
from repository.mongo.user import UsersRepository
from repository.mongo.warehouse import WarehouseRepository


async def update_stock(bot: Bot, users_repo: UsersRepository, warehouse_repo: WarehouseRepository):
    while True:
        now_moscow = datetime.now()
        date_from = int((now_moscow - timedelta(minutes=10)).timestamp())
        users = users_repo.get_all_users()
        for user in users:
            if "wb_key" not in user:
                continue
            new_orders = get_orders(user["wb_key"], date_from)["orders"]
            print(new_orders)
            for order in new_orders:
                print(order)
                res = warehouse_repo.get_article(order["article"])
                if res is None:
                    continue
                warehouse_repo.set_new_limit(order["article"], int(res["article"]["limit"]) - 1)
                if res["article"]["limit"] - 1 <= res["article"]["lower_limit"]:
                    await bot.send_message(res["user_id"],
                                           f"У вас заканчивается {res['article']['name']}! Осталось штук - {res['article']['limit'] - 1 }\n"
                                           f"Ваш нижний порог - {res['article']['lower_limit']}\n")
                print("Лимит уменьшен")
        await asyncio.sleep(60*10)
