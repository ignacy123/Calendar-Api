#!/bin/python3

import requests

URL = "http://127.0.0.1:5000/fav"

PARAMS = {"name": "golf"}

#r = requests.get(url = URL, params = PARAMS)
r = requests.delete(url = URL, params = PARAMS)

print("Status code:", r.status_code)

if r.status_code == 200:
    data = r.json()
    print(data)
else:
    print(str(r.content)[1:])
