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
    req = requests.get(url, headers=headers, params=params)
    if req.status_code != 200:
        print(f"Error: {req.status_code} - {req.text}")
        return None
    return req.json()
