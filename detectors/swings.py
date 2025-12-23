from typing import List, Tuple, Dict


def find_swings(candles: List[Dict]) -> Tuple[List[int], List[int]]:
    """
    Simple swing detection:
    - swing high: high[i] > high[i-1] and high[i] > high[i+1]
    - swing low : low[i]  < low[i-1]  and low[i]  < low[i+1]
    Returns (swing_high_indices, swing_low_indices).
    """
    n = len(candles)
    swing_highs: List[int] = []
    swing_lows: List[int] = []

    for i in range(1, n - 1):
        if (
            candles[i]["high"] > candles[i - 1]["high"]
            and candles[i]["high"] > candles[i + 1]["high"]
        ):
            swing_highs.append(i)

        if (
            candles[i]["low"] < candles[i - 1]["low"]
            and candles[i]["low"] < candles[i + 1]["low"]
        ):
            swing_lows.append(i)

    return swing_highs, swing_lows
