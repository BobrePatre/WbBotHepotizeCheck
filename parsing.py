import json

import requests

url = "https://statistics-api.wildberries.ru/"

headers = {
    "Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwNTA2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTczMzU1OTI"
                     "0NCwiaWQiOiIzODI4MGYxYS0wZWIzLTQ4N2UtOWMwMi01OGMzMTJlMmI0ZDAiLCJpaWQiOjExNzMxNjQ5MSwib2lkIjoxM"
                     "zg3NzI5LCJzIjoxMDczNzQxODU2LCJzaWQiOiJhZGMyNjg3OS0wZGJlLTRlOGItOGZkZC1hN2JkMzE0Y2Q1YmEiLCJ0Ijp"
                     "mYWxzZSwidWlkIjoxMTczMTY0OTF9.dIYPMS_p18cKIK6mzkwnFKT47CJcJ_Qfhw5TW12t589Zejx-J30AqyDyv3RePKGX"
                     "xIy0K-2Qbo4iNTDJMeCOZw",
}


def parse_data():
    response = requests.get(f"{url}api/v1/supplier/orders?dateFrom=2024-06-07&flag=1", headers=headers)
    if response.status_code == 429:
        print(response.headers["Content-Type"])
        raise Exception("rate limit reached")
    json_resp = json.loads(response.text)
    for item in json_resp:
        print(f"item raw: {item}")
    return json_resp
