import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from gateway.warehouse import get_orders
from repository.user import UsersRepository
from repository.warehouse import WarehouseRepository


async def process_order(bot, user, order, warehouse_repo):
    logging.info(f"Processing order {order['id']} for article {order['article']}")
    try:
        article_data = await warehouse_repo.get_article(order["article"])
    except Exception as e:
        logging.error(f"Failed to fetch article data for article {order['article']}: {e}")
        return

    if article_data is None:
        logging.warning(f"Article {order['article']} not found in warehouse. Skipping.")
        return

    try:
        current_limit = int(article_data["article"]["limit"])
        new_limit = current_limit - 1
        await warehouse_repo.set_new_limit(order["article"], new_limit)
        logging.info(f"Article {order['article']} limit updated: {current_limit} -> {new_limit}")

        if new_limit <= article_data["article"]["lower_limit"]:
            await bot.send_message(
                article_data["user_id"],
                f"У вас заканчивается {article_data['article']['name']}! Осталось штук - {new_limit}\n"
                f"Ваш нижний порог - {article_data['article']['lower_limit']}\n"
            )
            logging.info(f"Notification sent to user {article_data['user_id']} for article {order['article']}")
    except Exception as e:
        logging.error(f"Failed to update limit or send notification for article {order['article']}: {e}")


async def process_user(bot, user, date_from, warehouse_repo):
    if "wb_key" not in user:
        logging.warning(f"User {user['tg_id']} does not have a wb_key. Skipping.")
        return

    try:
        new_orders = await get_orders(user["wb_key"], date_from)
    except Exception as e:
        logging.error(f"Failed to fetch orders for user {user['tg_id']}: {e}")
        return

    if "orders" not in new_orders:
        logging.warning(f"No 'orders' in response for user {user['tg_id']}. Response: {new_orders}")
        return

    new_orders = new_orders["orders"]
    logging.info(f"User {user['tg_id']} - New orders fetched: {new_orders}")

    tasks = []
    for order in new_orders:
        tasks.append(process_order(bot, user, order, warehouse_repo))
    await asyncio.gather(*tasks)


async def update_stock(bot: Bot, users_repo: UsersRepository, warehouse_repo: WarehouseRepository):
    logging.info("Update Stock Task Triggered")

    now_moscow = datetime.now()
    date_from = int((now_moscow - timedelta(minutes=9, seconds=40)).timestamp())

    try:
        users = users_repo.get_all_users()
    except Exception as e:
        logging.error(f"Failed to fetch users: {e}")
        return

    tasks = []
    for user in users:
        tasks.append(process_user(bot, user, date_from, warehouse_repo))

    await asyncio.gather(*tasks)

    logging.info("Update Stock Task Completed")
