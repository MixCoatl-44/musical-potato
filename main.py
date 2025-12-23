from datetime import datetime, timezone
from typing import Dict, List

from utils.binance import get_klines
from utils.telegram import send_message
from detectors.setup1 import detect_setup1
from detectors.setup2 import detect_setup2

SYMBOLS = ["BTCUSDT", "ETHUSDT"]

TIMEFRAMES_SETUP1 = ["1m", "3m", "1d", "1w"]
TIMEFRAMES_SETUP2 = ["15m", "1h", "4h"]

# How many most-recent candles to consider "new" for alerts per timeframe.
# Tune these based on how often the workflow runs (hourly right now).
RECENT_BARS: Dict[str, int] = {
    "1m": 60,   # last hour
    "3m": 20,   # last hour
    "15m": 8,   # last 2 hours
    "1h": 3,    # last 3 hours
    "4h": 2,    # may create duplicates across runs
    "1d": 2,    # may create duplicates across runs
    "1w": 2,    # may create duplicates across runs
}


def format_time(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def build_message(signal: Dict, candles: List[Dict]) -> str:
    idx = signal["trigger_index"]
    c = candles[idx]
    direction = signal["direction"]
    setup = signal["setup"]
    symbol = signal["symbol"]
    tf = signal["timeframe"]

    price = c["close"]
    time_str = format_time(c["close_time"])

    msg = (
        f"Setup {setup} {direction.upper()} signal\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: {tf}\n"
        f"Trigger close time: {time_str}\n"
        f"Trigger price (close): {price:.2f}\n"
    )
    return msg


def run_for_combo(symbol: str, timeframe: str, setup_id: int) -> None:
    candles = get_klines(symbol, timeframe, limit=500)
    if len(candles) < 50:
        return

    if setup_id == 1:
        signals = detect_setup1(candles, symbol, timeframe)
    else:
        signals = detect_setup2(candles, symbol, timeframe)

    if not signals:
        return

    # Only alert on relatively recent triggers to avoid historic spam
    last_index = len(candles) - 1
    recent_bars = RECENT_BARS.get(timeframe, 5)

    for sig in signals:
        if last_index - sig["trigger_index"] < recent_bars:
            msg = build_message(sig, candles)
            print("ALERT:\n", msg)
            send_message(msg)


def main() -> None:
    # Setup 1
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES_SETUP1:
            try:
                run_for_combo(symbol, tf, setup_id=1)
            except Exception as e:
                print(f"Error in Setup 1 for {symbol} {tf}: {e}")

    # Setup 2
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES_SETUP2:
            try:
                run_for_combo(symbol, tf, setup_id=2)
            except Exception as e:
                print(f"Error in Setup 2 for {symbol} {tf}: {e}")


if __name__ == "__main__":
    main()
