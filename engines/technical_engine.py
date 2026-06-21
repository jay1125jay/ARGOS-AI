def ema(values, period):
    if not values:
        return 0

    k = 2 / (period + 1)
    result = values[0]

    for price in values[1:]:
        result = price * k + result * (1 - k)

    return round(result, 6)


def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0

    gains = []
    losses = []

    for i in range(-period, 0):
        change = closes[i] - closes[i - 1]
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def calc_atr_pct(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return 0.0

    trs = []

    for i in range(-period, 0):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    atr = sum(trs) / period
    return round((atr / closes[-1]) * 100, 4)


def volume_ratio(volumes, period=20):
    if len(volumes) < period + 1:
        return 1.0

    avg_volume = sum(volumes[-period - 1:-1]) / period

    if avg_volume == 0:
        return 1.0

    return round(volumes[-1] / avg_volume, 4)


def build_signal(symbol, candles):
    highs = [float(c[2]) for c in candles]
    lows = [float(c[3]) for c in candles]
    closes = [float(c[4]) for c in candles]
    volumes = [float(c[5]) for c in candles]

    price = closes[-1]
    prev_price = closes[-2]
    change_pct = round(((price - prev_price) / prev_price) * 100, 4)

    rsi = calc_rsi(closes)
    ema9 = ema(closes[-30:], 9)
    ema21 = ema(closes[-50:], 21)
    atr_pct = calc_atr_pct(highs, lows, closes)
    vol_ratio = volume_ratio(volumes)

    trend = "UP" if ema9 > ema21 else "DOWN" if ema9 < ema21 else "FLAT"

    signal_score = 50

    if trend == "UP":
        signal_score += 15
    if trend == "DOWN":
        signal_score -= 15

    if change_pct > 0:
        signal_score += 10
    if change_pct < 0:
        signal_score -= 10

    if rsi >= 55:
        signal_score += 10
    if rsi <= 45:
        signal_score -= 10

    if vol_ratio >= 1.2:
        if trend == "UP":
            signal_score += 10
        elif trend == "DOWN":
            signal_score -= 10

    signal_score = max(0, min(100, signal_score))

    risk_score = 20

    if atr_pct >= 1.0:
        risk_score += 30

    if rsi >= 80 or rsi <= 20:
        risk_score += 30

    if vol_ratio < 0.5:
        risk_score += 10

    risk_score = max(0, min(100, risk_score))

    price_above_ema9 = price > ema9
    price_below_ema9 = price < ema9

    long_ready = (
        trend == "UP"
        and signal_score >= 75
        and rsi >= 55
        and vol_ratio >= 1.2
        and atr_pct >= 0.05
        and price_above_ema9
    )

    short_ready = (
        trend == "DOWN"
        and signal_score <= 25
        and rsi <= 45
        and vol_ratio >= 1.2
        and atr_pct >= 0.05
        and price_below_ema9
    )

    if risk_score >= 70:
        action = "WAIT"
    elif long_ready:
        action = "LONG"
    elif short_ready:
        action = "SHORT"
    else:
        action = "WAIT"

    return {
        "symbol": symbol,
        "price": price,
        "change_pct": change_pct,
        "rsi": rsi,
        "ema9": ema9,
        "ema21": ema21,
        "trend": trend,
        "volume_ratio": vol_ratio,
        "atr_pct": atr_pct,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "action": action,
    }