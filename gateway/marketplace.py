import logging
import aiohttp

host = "https://marketplace-api.wildberries.ru"


async def fetch_orders(date_from, date_to, token):
    headers = {
        'accept': 'application/json',
        'Authorization': token
    }
    params = {
        'limit': 1000,
        'next': 0,
        'dateFrom': date_from,
        'dateTo': date_to
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(host + "/api/v3/orders", headers=headers, params=params) as response:
            logging.debug(f"Fetching orders response: {response.status}")
            if response.status != 200:
                logging.error(f"Error fetching orders: {response.status} - {await response.text()}")
                return None
            logging.debug(f"Fetching orders response: {await response.text()}")
            return (await response.json())["orders"]
