from typing import List, Dict, Tuple
from .swings import find_swings


def _build_swing_points(
    swing_highs: List[int], swing_lows: List[int]
) -> List[Tuple[int, str]]:
    points: List[Tuple[int, str]] = []
    for idx in swing_highs:
        points.append((idx, "H"))
    for idx in swing_lows:
        points.append((idx, "L"))
    points.sort(key=lambda x: x[0])
    return points


def detect_setup2(candles: List[Dict], symbol: str, timeframe: str) -> List[Dict]:
    """
    Detect Setup 2 (both bullish and bearish).

    Bearish:
      - Swings: L0 - H1 - L2 - H3 (exactly this alternating order).
      - H3 > H1 and between H1 and H3 no other candle's high > H1.
      - Next candle after H3 does NOT make a higher high.
      - After H3, at some candle C, close[C] < low[0] (close below starting point).
        -> Alert at candle C.

    Bullish: mirror (H0 - L1 - H2 - L3), sweep below L1, then close above H0.
    """
    n = len(candles)
    swing_highs, swing_lows = find_swings(candles)
    points = _build_swing_points(swing_highs, swing_lows)
    total_points = len(points)
    signals: List[Dict] = []

    if total_points < 4:
        return signals

    for k in range(total_points - 3):
        (i0, t0), (i1, t1), (i2, t2), (i3, t3) = points[k : k + 4]
        if not (i0 < i1 < i2 < i3):
            continue

        # ----- Bearish: L-H-L-H -----
        if t0 == "L" and t1 == "H" and t2 == "L" and t3 == "H":
            low0 = candles[i0]["low"]
            high1 = candles[i1]["high"]
            high3 = candles[i3]["high"]

            if high3 <= high1:
                continue

            # Only candle that trades above high1 is at i3
            swept_ok = True
            for j in range(i1 + 1, i3):
                if candles[j]["high"] > high1:
                    swept_ok = False
                    break
            if not swept_ok:
                continue

            # Next candle does not make higher high
            if i3 + 1 < n and candles[i3 + 1]["high"] > high3:
                continue

            # Confirmation: close below starting low0
            for iC in range(i3 + 1, n):
                if candles[iC]["close"] < low0:
                    signals.append(
                        {
                            "setup": "2",
                            "direction": "bearish",
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "trigger_index": iC,
                            "trigger_time": candles[iC]["close_time"],
                            "info": {
                                "start_index": i0,
                                "swing1_index": i1,
                                "swing2_index": i2,
                                "sweep_index": i3,
                            },
                        }
                    )
                    break

        # ----- Bullish: H-L-H-L -----
        if t0 == "H" and t1 == "L" and t2 == "H" and t3 == "L":
            high0 = candles[i0]["high"]
            low1 = candles[i1]["low"]
            low3 = candles[i3]["low"]

            if low3 >= low1:
                continue

            # Only candle that trades below low1 is at i3
            swept_ok = True
            for j in range(i1 + 1, i3):
                if candles[j]["low"] < low1:
                    swept_ok = False
                    break
            if not swept_ok:
                continue

            # Next candle does not make lower low
            if i3 + 1 < n and candles[i3 + 1]["low"] < low3:
                continue

            # Confirmation: close above starting high0
            for iC in range(i3 + 1, n):
                if candles[iC]["close"] > high0:
                    signals.append(
                        {
                            "setup": "2",
                            "direction": "bullish",
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "trigger_index": iC,
                            "trigger_time": candles[iC]["close_time"],
                            "info": {
                                "start_index": i0,
                                "swing1_index": i1,
                                "swing2_index": i2,
                                "sweep_index": i3,
                            },
                        }
                    )
                    break

    return signals
