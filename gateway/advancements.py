import logging
import aiohttp

host = "https://advert-api.wildberries.ru"


async def get_advancements(token):
    url = host + "/adv/v1/promotion/count"
    headers = {
        "Authorization": f"{token}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logging.error(f"Error: {response.status} - {await response.text()}")
                return None
            return await response.json()


async def get_advancement_budget(token: str, advencement_id: int):
    url = host + "/adv/v1/budget"
    headers = {
        "Authorization": f"{token}"
    }
    params = {
        "id": advencement_id,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                logging.error(f"Error: {response.status} - {await response.text()}")
                return None
            return await response.json()


async def get_advancement_data(token: str, advencement_id: int):
    url = host + "/adv/v1/promotion/adverts"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    response_body = [
        advencement_id,
    ]
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=response_body) as response:
            if response.status != 200:
                logging.error(f"Error: {response.status} - {await response.text()}")
                return None
            return await response.json()


async def get_advancement_cost_history(token: str, from_date, to_date):
    url = host + "/adv/v1/upd"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    parameters = {
        "from": from_date,
        "to": to_date,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=parameters) as response:
            if response.status != 200:
                logging.error(f"Error: {response.status} - {await response.text()}")
                return None
            return await response.json()
