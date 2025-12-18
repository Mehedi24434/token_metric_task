import time
import requests

BASE_URL = "https://api.hyperliquid.xyz/info"

def fetch_mids():
    r = requests.post(BASE_URL, json={"type": "allMids"}, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_orderbook(asset):
    r = requests.post(BASE_URL, json={"type": "l2Book", "coin": asset}, timeout=10)
    r.raise_for_status()
    return r.json()

    now = time.time() * 1000
    return sum(float(t["sz"]) for t in trades if now - t["time"] <= lookback_seconds * 1000)
