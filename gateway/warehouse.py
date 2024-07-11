import requests

host = "https://suppliers-api.wildberries.ru"


def get_orders(token, date_from):
    url = host + "/api/v3/orders"
    headers = {
        "Authorization": f"{token}"
    }
    params = {
        "limit": 1000,
        "next": 0,
        "dateFrom": f"{date_from}"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        response.raise_for_status()
        return None
    return response.json()
