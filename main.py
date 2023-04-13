# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : main.py                 #
# ----------------------------------------------- #

import json
import time

from fastapi import FastAPI, Request

import config
from handler import *

app = FastAPI()


def get_timestamp():
    timestamp = time.strftime("%Y-%m-%d %X")
    return timestamp


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    headers = request.headers
    if 'text/plain' in headers['content-type']:
        raise ValueError('Alert Message must be of type application/json')
    elif 'application/json' in headers['content-type']:
        data = await request.json()
        print("[*]", get_timestamp(), "Alert Received: ", data)
        if 'key' not in data:
            print("[X]", get_timestamp(), "Access Refused! Message must contain the 'key'")
            return 400
        key = data['key']
        if key == config.sec_key:
            await send_alert(data)
            return 200
        else:
            print("[X]", get_timestamp(), "Alert Received & Refused! (Wrong Key)")
            return 400
