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


def build_argos_state(score, bias, permission, reasons):
    if permission == "BLOCK":
        return {
            "argos_state": "BLOCKED",
            "argos_message": "ARGOS hard blocked trading by extreme risk.",
            "auto_ready": False
        }

    if permission == "DEFENSIVE":
        return {
            "argos_state": "CAUTION",
            "argos_message": "ARGOS allows only defensive paper setups.",
            "auto_ready": False
        }

    if score >= 70 and bias == "BULLISH":
        return {
            "argos_state": "READY_LONG",
            "argos_message": "ARGOS is ready for a long setup.",
            "auto_ready": True
        }

    if score >= 70 and bias == "BEARISH":
        return {
            "argos_state": "READY_SHORT",
            "argos_message": "ARGOS is ready for a short setup.",
            "auto_ready": True
        }

    return {
        "argos_state": "ANALYZING",
        "argos_message": "ARGOS is analyzing market conditions.",
        "auto_ready": False
    }


def update_ai_status():
    news = load_json(NEWS_FILE, {})
    macro = load_json(MACRO_FILE, {})
    regime = load_json(REGIME_FILE, {})

    score = 50
    reasons = []

    news_sentiment = str(news.get("market_sentiment", "NEUTRAL")).upper()
    news_risk = str(news.get("risk_level", "NORMAL")).upper()

    macro_regime = str(macro.get("market_regime", "NEUTRAL")).upper()
    macro_risk = str(macro.get("event_risk", "NORMAL")).upper()

    market_regime = str(regime.get("market_regime", "SIDEWAYS")).upper()
    volatility = str(regime.get("volatility", "NORMAL")).upper()

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
    elif macro_risk == "EXTREME":
        score -= 40
        reasons.append("MACRO_EXTREME_RISK")

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

    if score >= 65:
        bias = "BULLISH"
    elif score <= 35:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    extreme_block = (
        "MACRO_EXTREME_RISK" in reasons
        or news_risk == "EXTREME"
    )

    if extreme_block:
        permission = "BLOCK"
        risk_mode = "HARD_BLOCK"
    elif score <= 35:
        permission = "DEFENSIVE"
        risk_mode = "DEFENSIVE"
    elif score >= 65:
        permission = "ALLOW"
        risk_mode = "AGGRESSIVE"
    else:
        permission = "WAIT"
        risk_mode = "NORMAL"

    state = build_argos_state(score, bias, permission, reasons)

    data = {
        "mode": "ARGOS_UNIFIED_AI_V2",
        "ai_bias": bias,
        "confidence": score,
        "trade_permission": permission,
        "risk_mode": risk_mode,
        "reason": ",".join(reasons),
        "argos_state": state["argos_state"],
        "argos_message": state["argos_message"],
        "auto_ready": state["auto_ready"]
    }

    os.makedirs(os.path.dirname(AI_FILE), exist_ok=True)

    with open(AI_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def load_ai_status():
    return update_ai_status()


if __name__ == "__main__":
    result = update_ai_status()
    print("ARGOS_AI_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("STATE=" + result["argos_state"])
    print("BIAS=" + result["ai_bias"])
    print("CONFIDENCE=" + str(result["confidence"]))
    print("PERMISSION=" + result["trade_permission"])
    print("RISK_MODE=" + result["risk_mode"])
    print("AUTO_READY=" + str(result["auto_ready"]))
    print("MESSAGE=" + result["argos_message"])