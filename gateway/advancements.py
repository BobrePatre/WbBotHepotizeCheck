import logging

import requests

host = "https://advert-api.wb.ru"


def get_advancements(token):
    url = host + "/adv/v1/promotion/count"
    headers = {
        "Authorization": f"{token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        return None
    return response.json()


def get_advancement_budget(token: str, advencement_id: int):
    url = host + "/adv/v1/budget"
    headers = {
        "Authorization": f"{token}"
    }
    params = {
        "id": advencement_id,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logging.error(f"Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        return None
    return response.json()


def get_advancement_data(token: str, advencement_id: int):
    url = host + "/adv/v1/promotion/adverts"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    response_body = [
        advencement_id,
    ]
    response = requests.post(url, headers=headers, json=response_body)
    if response.status_code != 200:
        logging.error(f"Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        return None
    return response.json()


def get_advancement_cost_history(token: str, from_date, to_date):
    url = host + "/adv/v1/upd"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    parameters = {
        "from": from_date,
        "to": to_date,
    }
    response = requests.get(url, headers=headers, params=parameters)
    if response.status_code != 200:
        logging.error(f"Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        return None
    return response.json()
