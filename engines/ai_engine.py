import json
import os

BASE_DIR = r"C:\ARGOS_AI"

NEWS_FILE = os.path.join(BASE_DIR, "data", "news", "news_status.json")
MACRO_FILE = os.path.join(BASE_DIR, "data", "macro", "macro_status.json")
REGIME_FILE = os.path.join(BASE_DIR, "data", "market", "regime_status.json")
AI_FILE = os.path.join(BASE_DIR, "data", "ai", "ai_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_ai_status():
    news = load_json(NEWS_FILE, {})
    macro = load_json(MACRO_FILE, {})
    regime = load_json(REGIME_FILE, {})

    score = 50
    reasons = []

    news_sentiment = news.get("market_sentiment", "NEUTRAL")
    news_risk = news.get("risk_level", "NORMAL")
    macro_regime = macro.get("market_regime", "NEUTRAL")
    macro_risk = macro.get("event_risk", "NORMAL")
    market_regime = regime.get("market_regime", "SIDEWAYS")
    volatility = regime.get("volatility", "NORMAL")

    if news_sentiment == "POSITIVE":
        score += 15
        reasons.append("NEWS_POSITIVE")
    elif news_sentiment == "NEGATIVE":
        score -= 15
        reasons.append("NEWS_NEGATIVE")

    if news_risk == "HIGH":
        score -= 15
        reasons.append("NEWS_HIGH_RISK")
    elif news_risk == "WATCH":
        score -= 5
        reasons.append("NEWS_WATCH")

    if macro_regime == "RISK_ON":
        score += 15
        reasons.append("MACRO_RISK_ON")
    elif macro_regime == "RISK_OFF":
        score -= 15
        reasons.append("MACRO_RISK_OFF")

    if macro_risk == "HIGH":
        score -= 15
        reasons.append("MACRO_HIGH_RISK")
    elif macro_risk == "WATCH":
        score -= 5
        reasons.append("MACRO_WATCH")

    if market_regime == "BULL":
        score += 15
        reasons.append("MARKET_BULL")
    elif market_regime == "BEAR":
        score -= 15
        reasons.append("MARKET_BEAR")

    if volatility == "HIGH":
        score -= 10
        reasons.append("VOL_HIGH")

    score = max(0, min(100, score))

    if score >= 70:
        bias = "BULLISH"
    elif score <= 30:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    if score <= 30:
        permission = "BLOCK"
        risk_mode = "DEFENSIVE"
    elif score >= 70:
        permission = "ALLOW"
        risk_mode = "AGGRESSIVE"
    else:
        permission = "ALLOW"
        risk_mode = "NORMAL"

    data = {
        "mode": "UNIFIED_AI_V1",
        "ai_bias": bias,
        "confidence": score,
        "trade_permission": permission,
        "risk_mode": risk_mode,
        "reason": ",".join(reasons)
    }

    os.makedirs(os.path.dirname(AI_FILE), exist_ok=True)

    with open(AI_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def load_ai_status():
    return update_ai_status()


if __name__ == "__main__":
    result = update_ai_status()
    print("UNIFIED_AI_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("BIAS=" + result["ai_bias"])
    print("CONFIDENCE=" + str(result["confidence"]))
    print("PERMISSION=" + result["trade_permission"])
    print("RISK_MODE=" + result["risk_mode"])
    print("REASON=" + result["reason"])
