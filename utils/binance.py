import requests
from typing import List, Dict

BASE_URL = "https://api.binance.com"


def get_klines(symbol: str, interval: str, limit: int = 500) -> List[Dict]:
    """
    Fetch OHLCV candles from Binance and return as a list of dicts.
    """
    url = f"{BASE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    raw = resp.json()

    candles: List[Dict] = []
    for k in raw:
        candles.append(
            {
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6],
            }
        )
    return candles
