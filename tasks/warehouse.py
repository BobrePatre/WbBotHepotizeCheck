import logging
from datetime import datetime, timedelta
from aiogram import Bot

from gateway.warehouse import get_orders
from repository.user import UsersRepository
from repository.warehouse import WarehouseRepository


async def update_stock(bot: Bot, users_repo: UsersRepository, warehouse_repo: WarehouseRepository):
    logging.info("Update Stock Task Triggered")

    now_moscow = datetime.now()
    date_from = int((now_moscow - timedelta(minutes=9, seconds=40)).timestamp())

    try:
        users = users_repo.get_all_users()
    except Exception as e:
        logging.error(f"Failed to fetch users: {e}")
        return

    for user in users:
        if "wb_key" not in user:
            logging.warning(f"User {user['tg_id']} does not have a wb_key. Skipping.")
            continue

        try:
            new_orders = get_orders(user["wb_key"], date_from)
        except Exception as e:
            logging.error(f"Failed to fetch orders for user {user['tg_id']}: {e}")
            continue

        if "orders" not in new_orders:
            logging.warning(f"No 'orders' in response for user {user['tg_id']}. Response: {new_orders}")
            continue

        new_orders = new_orders["orders"]
        logging.info(f"User {user['tg_id']} - New orders fetched: {new_orders}")

        for order in new_orders:
            logging.info(f"Processing order {order['user_id']} for article {order['article']}")

            try:
                article_data = warehouse_repo.get_article(order["article"])
            except Exception as e:
                logging.error(f"Failed to fetch article data for article {order['article']}: {e}")
                continue

            if article_data is None:
                logging.warning(f"Article {order['article']} not found in warehouse. Skipping.")
                continue

            try:
                current_limit = int(article_data["article"]["limit"])
                new_limit = current_limit - 1
                warehouse_repo.set_new_limit(order["article"], new_limit)
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

    logging.info("Update Stock Task Completed")
