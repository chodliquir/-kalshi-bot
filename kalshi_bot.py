import requests

import time

import os

from datetime import datetime

API_KEY = os.getenv("API_KEY")

API_SECRET = os.getenv("API_SECRET")

BASE_URL = "https://api.kalshi.com/trade-api/v2"

MAX_OPEN_TRADES = 5

TRADE_SIZE = 1

PROFIT_TARGET = 5

STOP_LOSS = 8

open_trades = []

def get_headers():

    return {

        "Content-Type": "application/json",

        "API-KEY": API_KEY

    }

def get_markets():

    try:

        r = requests.get(f"{BASE_URL}/markets", headers=get_headers())

        return r.json().get("markets", [])

    except Exception as e:

        print("Market fetch error:", e)

        return []

def place_order(ticker, side, price, size):

    payload = {

        "ticker": ticker,

        "action": side,

        "price": price,

        "count": size,

        "type": "limit"

    }

    try:

        r = requests.post(

            f"{BASE_URL}/portfolio/orders",

            headers=get_headers(),

            json=payload

        )

        print("Order response:", r.text)

    except Exception as e:

        print("Order error:", e)

def is_valid_market(m):

    try:

        yes_ask = m["yes_ask"]

        yes_bid = m["yes_bid"]

        volume = m.get("volume", 0)

        return (

            30 <= yes_ask <= 60 and

            (yes_ask - yes_bid) <= 4 and

            volume > 1000

        )

    except:

        return False

def try_enter_trade(m):

    global open_trades

    if len(open_trades) >= MAX_OPEN_TRADES:

        return

    ticker = m["ticker"]

    price = m["yes_ask"]

    if any(t["ticker"] == ticker for t in open_trades):

        return

    print(f"BUY {ticker} @ {price}")

    place_order(ticker, "buy", price, TRADE_SIZE)

    open_trades.append({

        "ticker": ticker,

        "entry": price,

        "target": price + PROFIT_TARGET,

        "stop": price - STOP_LOSS,

        "time": datetime.now()

    })

def check_exits(markets):

    global open_trades

    remaining = []

    for t in open_trades:

        m = next((x for x in markets if x["ticker"] == t["ticker"]), None)

        if not m:

            continue

        price = m["yes_bid"]

        if price >= t["target"]:

            print(f"TAKE PROFIT {t['ticker']} @ {price}")

            place_order(t["ticker"], "sell", price, TRADE_SIZE)

        elif price <= t["stop"]:

            print(f"STOP LOSS {t['ticker']} @ {price}")

            place_order(t["ticker"], "sell", price, TRADE_SIZE)

        else:

            remaining.append(t)

    open_trades = remaining

def run_bot():

    print("Bot started...")

    while True:

        markets = get_markets()

        check_exits(markets)

        for m in markets:

            if is_valid_market(m):

                try_enter_trade(m)

        print(f"Open trades: {len(open_trades)}")

        time.sleep(30)

if __name__ == "__main__":

    run_bot(
