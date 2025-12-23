from typing import List, Dict
from .swings import find_swings

# Heuristic parameters – you can tune these
BASE_LOOKBACK_MAX = 10      # how far back we search for a base before the high/low
BASE_LOOKBACK_MIN = 3       # leave at least 3 candles between base and swing point
WICK_LOOKAHEAD = 10         # how many candles after the swing we search for wick retest
CONTINUATION_LOOKAHEAD = 15 # how many candles after wick we look for break


def detect_setup1(candles: List[Dict], symbol: str, timeframe: str) -> List[Dict]:
    """
    Detect Setup 1 (both bullish and bearish).

    Bullish:
      - Find swing high H.
      - Define a 'base' in the window [H-BASE_LOOKBACK_MAX ... H-BASE_LOOKBACK_MIN].
      - After H, find ONE candle whose low <= base_low and whose next candle's low > base_low
        (single wick retest into/below base).
      - After that wick, find a candle that breaks above the high of H.
        -> Alert when that continuation candle closes.

    Bearish is the mirror image.
    """
    n = len(candles)
    swing_highs, swing_lows = find_swings(candles)
    signals: List[Dict] = []

    # --- Bullish version: rally-base-rally ---
    for iH in swing_highs:
        if iH < BASE_LOOKBACK_MAX or iH < BASE_LOOKBACK_MIN + 1:
            continue
        if iH >= n - (WICK_LOOKAHEAD + CONTINUATION_LOOKAHEAD + 1):
            # not enough candles after the high to fully form the pattern
            continue

        base_start = max(0, iH - BASE_LOOKBACK_MAX)
        base_end = iH - BASE_LOOKBACK_MIN
        if base_end <= base_start:
            continue

        base_slice = candles[base_start : base_end + 1]
        base_low = min(c["low"] for c in base_slice)
        base_high = max(c["high"] for c in base_slice)

        # Require that the swing high actually sticks out above the base
        if candles[iH]["high"] <= base_high:
            continue

        # Find wick retest into or below base_low
        wick_index = None
        for i in range(iH + 1, min(n - 2, iH + WICK_LOOKAHEAD)):
            if candles[i]["low"] <= base_low:
                # single test: next candle's low > base_low
                if candles[i + 1]["low"] > base_low:
                    wick_index = i
                    break
        if wick_index is None:
            continue

        # Find continuation: break above high of H
        break_index = None
        ref_high = candles[iH]["high"]
        for i in range(wick_index + 1, min(n, wick_index + CONTINUATION_LOOKAHEAD)):
            if candles[i]["high"] > ref_high:
                break_index = i
                break
        if break_index is None:
            continue

        signals.append(
            {
                "setup": "1",
                "direction": "bullish",
                "symbol": symbol,
                "timeframe": timeframe,
                "trigger_index": break_index,
                "trigger_time": candles[break_index]["close_time"],
                "info": {
                    "high_index": iH,
                    "wick_index": wick_index,
                    "base_start": base_start,
                    "base_end": base_end,
                    "base_low": base_low,
                },
            }
        )

    # --- Bearish version: drop-base-drop ---
    for iL in swing_lows:
        if iL < BASE_LOOKBACK_MAX or iL < BASE_LOOKBACK_MIN + 1:
            continue
        if iL >= n - (WICK_LOOKAHEAD + CONTINUATION_LOOKAHEAD + 1):
            continue

        base_start = max(0, iL - BASE_LOOKBACK_MAX)
        base_end = iL - BASE_LOOKBACK_MIN
        if base_end <= base_start:
            continue

        base_slice = candles[base_start : base_end + 1]
        base_low = min(c["low"] for c in base_slice)
        base_high = max(c["high"] for c in base_slice)

        # low should stick out below the base
        if candles[iL]["low"] >= base_low:
            continue

        # Wick retest upward into or above base_high
        wick_index = None
        for i in range(iL + 1, min(n - 2, iL + WICK_LOOKAHEAD)):
            if candles[i]["high"] >= base_high:
                if candles[i + 1]["high"] < base_high:
                    wick_index = i
                    break
        if wick_index is None:
            continue

        # Continuation: break below low of L
        break_index = None
        ref_low = candles[iL]["low"]
        for i in range(wick_index + 1, min(n, wick_index + CONTINUATION_LOOKAHEAD)):
            if candles[i]["low"] < ref_low:
                break_index = i
                break
        if break_index is None:
            continue

        signals.append(
            {
                "setup": "1",
                "direction": "bearish",
                "symbol": symbol,
                "timeframe": timeframe,
                "trigger_index": break_index,
                "trigger_time": candles[break_index]["close_time"],
                "info": {
                    "low_index": iL,
                    "wick_index": wick_index,
                    "base_start": base_start,
                    "base_end": base_end,
                    "base_high": base_high,
                },
            }
        )

    return signals
