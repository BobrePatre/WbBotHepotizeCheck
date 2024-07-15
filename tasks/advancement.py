import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from repository.advancement import AdvancementRepository
from gateway.advancements import get_advancements, get_advancement_budget, get_advancement_data
from repository.user import UsersRepository


async def process_advert(bot, user, advancement, advert):
    logging.info("Processing advert: %s", advert)
    for advert_data in advert['advert_list']:
        resp = await get_advancement_budget(user["wb_key"], advert_data['advertId'])
        if resp is None:
            logging.warning("No budget info for advert: %s", advert_data['advertId'])
            continue

        current_budget = int(resp["total"])
        min_amount = int(advancement['min_amount'])

        if current_budget <= min_amount and current_budget != 0:
            adv_data = await get_advancement_data(user["wb_key"], advert_data['advertId'])
            adv_name = adv_data[0]['name'] if adv_data else 'Unknown'
            await bot.send_message(
                advancement["user_id"],
                f"У вас кончается бюджет на рекламной компании с id: {advert_data['advertId']}.\n"
                f"Ваш минимальный бюджет: {min_amount}\n"
                f"Остаток на компании: {current_budget}\n"
                f"Имя компании: {adv_name}"
            )
            logging.info("Notification sent for advert: %s", advert_data['advertId'])


async def process_user(bot, user, advancement):
    logging.info("Fetching advancements for user: %s", user["tg_id"])
    res = await get_advancements(user["wb_key"])
    if not res or "adverts" not in res:
        logging.info("No adverts found for user: %s", user["tg_id"])
        return

    for advert in res['adverts']:
        await process_advert(bot, user, advancement, advert)
        await asyncio.sleep(120)  # Используйте await для асинхронного сна


async def check_advancement(bot: Bot, advancement_repo: AdvancementRepository, user_repository: UsersRepository):
    logging.info("Check Advancement Task Triggered at %s", datetime.now())

    users_advancements = advancement_repo.get_all_advancements()
    logging.info("Fetched all advancements: %d advancements found", len(users_advancements))

    tasks = []
    for advancement in users_advancements:
        user = user_repository.get_user(advancement['user_id'])
        if not user or "wb_key" not in user:
            logging.warning("Skipping advancement for user without wb_key: %s", advancement['user_id'])
            continue

        tasks.append(process_user(bot, user, advancement))

    await asyncio.gather(*tasks)

