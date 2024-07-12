import logging

import requests

host = "https://marketplace-api.wildberries.ru"


def fetch_orders(date_from, date_to, token):
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

    response = requests.get(host + "/api/v3/orders", headers=headers, params=params)
    logging.debug(f" fething orders response: {response.status_code}")
    if response.status_code != 200:
        response.raise_for_status()
        return None
    logging.debug(f"fething orders response: {response.text}")
    return response.json()["orders"]
