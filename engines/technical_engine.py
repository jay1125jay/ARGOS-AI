import math


def to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def extract_ohlcv(candles):
    closes = []
    highs = []
    lows = []
    volumes = []

    for c in candles:
        highs.append(to_float(c[2]))
        lows.append(to_float(c[3]))
        closes.append(to_float(c[4]))
        volumes.append(to_float(c[5]))

    return highs, lows, closes, volumes


def ema(values, period):
    if not values:
        return 0

    k = 2 / (period + 1)
    result = values[0]

    for price in values[1:]:
        result = price * k + result * (1 - k)

    return round(result, 6)


def rsi(values, period=14):
    if len(values) < period + 1:
        return 50

    gains = []
    losses = []

    recent = values[-(period + 1):]

    for i in range(1, len(recent)):
        diff = recent[i] - recent[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def atr_pct(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return 0

    trs = []

    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        trs.append(tr)

    atr = sum(trs[-period:]) / period
    price = closes[-1]

    if price <= 0:
        return 0

    return round((atr / price) * 100, 4)


def volume_ratio(volumes, period=20):
    if len(volumes) < period + 1:
        return 0

    avg_volume = sum(volumes[-(period + 1):-1]) / period
    current_volume = volumes[-1]

    if avg_volume <= 0:
        return 0

    return round(current_volume / avg_volume, 4)


def detect_trend(ema9, ema21, rsi_value):
    if ema9 > ema21 and rsi_value >= 50:
        return "UP"

    if ema9 < ema21 and rsi_value <= 50:
        return "DOWN"

    return "FLAT"


def detect_entry_1m(ema9, ema21, rsi_value, vol_ratio):
    if ema9 > ema21 and rsi_value >= 52:
        return "LONG"

    if ema9 < ema21 and rsi_value <= 48:
        return "SHORT"

    return "WAIT"


def build_risk_score(atr_value, vol_ratio):
    risk = 20

    if atr_value >= 0.6:
        risk += 30
    elif atr_value >= 0.4:
        risk += 20
    elif atr_value >= 0.25:
        risk += 10

    if vol_ratio <= 0.05:
        risk += 20
    elif vol_ratio <= 0.15:
        risk += 10

    return min(risk, 100)


def build_signal_score(final_action, entry_signal_1m, trend_5m):
    if final_action == "LONG":
        return 85

    if final_action == "SHORT":
        return 15

    if entry_signal_1m == "LONG" and trend_5m == "UP":
        return 65

    if entry_signal_1m == "SHORT" and trend_5m == "DOWN":
        return 35

    return 50


def build_signal(symbol, candles_5m, candles_1m=None):
    if candles_1m is None:
        candles_1m = candles_5m

    highs_5m, lows_5m, closes_5m, volumes_5m = extract_ohlcv(candles_5m)
    highs_1m, lows_1m, closes_1m, volumes_1m = extract_ohlcv(candles_1m)

    price = closes_1m[-1] if closes_1m else 0
    prev_price = closes_1m[-2] if len(closes_1m) >= 2 else price

    change_pct = 0
    if prev_price:
        change_pct = round(((price - prev_price) / prev_price) * 100, 4)

    ema9_5m = ema(closes_5m[-50:], 9)
    ema21_5m = ema(closes_5m[-80:], 21)
    rsi_5m = rsi(closes_5m)

    ema9_1m = ema(closes_1m[-50:], 9)
    ema21_1m = ema(closes_1m[-80:], 21)
    rsi_1m = rsi(closes_1m)

    vol_ratio_1m = volume_ratio(volumes_1m)
    atr_1m = atr_pct(highs_1m, lows_1m, closes_1m)

    trend_5m = detect_trend(ema9_5m, ema21_5m, rsi_5m)
    entry_signal_1m = detect_entry_1m(ema9_1m, ema21_1m, rsi_1m, vol_ratio_1m)

    final_action = "WAIT"

    if trend_5m == "UP" and entry_signal_1m == "LONG":
        final_action = "LONG"

    elif trend_5m == "DOWN" and entry_signal_1m == "SHORT":
        final_action = "SHORT"

    risk_score = build_risk_score(atr_1m, vol_ratio_1m)
    signal_score = build_signal_score(final_action, entry_signal_1m, trend_5m)

    return {
        "symbol": symbol,
        "price": round(price, 6),
        "change_pct": change_pct,

        "rsi": rsi_1m,
        "ema9": ema9_1m,
        "ema21": ema21_1m,
        "trend": trend_5m,
        "volume_ratio": vol_ratio_1m,
        "atr_pct": atr_1m,

        "trend_5m": trend_5m,
        "rsi_5m": rsi_5m,
        "ema9_5m": ema9_5m,
        "ema21_5m": ema21_5m,

        "entry_signal_1m": entry_signal_1m,
        "rsi_1m": rsi_1m,
        "ema9_1m": ema9_1m,
        "ema21_1m": ema21_1m,

        "final_action": final_action,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "action": final_action
    }