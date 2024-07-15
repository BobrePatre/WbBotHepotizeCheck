import logging
import aiohttp

host = "https://suppliers-api.wildberries.ru"


async def get_orders(token, date_from):
    url = host + "/api/v3/orders"
    headers = {
        "Authorization": f"{token}"
    }
    params = {
        "limit": 1000,
        "next": 0,
        "dateFrom": f"{date_from}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                logging.error(f"Error: {response.status} - {await response.text()}")
                response.raise_for_status()
                return None
            return await response.json()

# Пример использования функции в асинхронном контексте
# import asyncio
# orders = asyncio.run(get_orders(token, date_from))
