import logging

import requests

host = "https://advert-api.wb.ru"


def get_advancements(token):
    url = host + "/adv/v1/promotion/count"
    headers = {
        "Authorization": f"{token}"
    }
    req = requests.get(url, headers=headers)
    if req.status_code != 200:
        print(f"Error: {req.status_code} - {req.text}")
        return None
    return req.json()


def get_advancement_budget(token: str, advencement_id: int):
    url = host + "/adv/v1/budget"
    headers = {
        "Authorization": f"{token}"
    }
    params = {
        "id": advencement_id,
    }
    req = requests.get(url, headers=headers, params=params)
    if req.status_code != 200:
        print(f"Error: {req.status_code} - {req.text}")
        return None
    return req.json()


def get_advancement_data(token: str, advencement_id: int):
    url = host + "/adv/v1/promotion/adverts"
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    req_body = [
        advencement_id,
    ]
    resp = requests.post(url, headers=headers, json=req_body)
    if resp.status_code != 200:
        print(f"Error: {resp.status_code} - {resp.text}")
        return None
    return resp.json()


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
