import asyncio

from aiogram import Bot

from repository.advancement import AdvancementRepository
from gateway.advancements import get_advancements, get_advancement_budget, get_advancement_data
from repository.user import UsersRepository


async def check_advancement(bot: Bot, advancement_repo: AdvancementRepository, user_repository: UsersRepository):
    while True:
        users_advancements = advancement_repo.get_all_advancements()
        for advancement in users_advancements:
            user = user_repository.get_user(advancement['user_id'])
            res = get_advancements(user["wb_key"])
            for advert in res['adverts']:
                asyncio.sleep(20)
                print(advert)
                for advert_data in advert['advert_list']:
                    resp = get_advancement_budget(user["wb_key"], advert_data['advertId'])
                    if resp is None:
                        continue
                    if int(resp["total"]) <= int(advancement['min_amount']):
                        if int(resp["total"]) == 0:
                            continue
                        adv_data = get_advancement_data(user["wb_key"], advert_data['advertId'])
                        await bot.send_message(advancement["user_id"],
                                               f"У вас кончается бюджет на рекламной компании с id: "
                                               f"{advert_data['advertId']}.\n"
                                               f"Ваш минимальный бюджет: {advancement['min_amount']}\n"
                                               f"Остаток на компании: {resp['total']}\n"
                                               f"Имя компании: {adv_data[0]['name']}")
        await asyncio.sleep(60*45)
