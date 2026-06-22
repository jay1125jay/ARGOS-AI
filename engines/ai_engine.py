import json
import os

BASE_DIR = r"C:\ARGOS_AI"

NEWS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "news",
    "news_status.json"
)

MACRO_FILE = os.path.join(
    BASE_DIR,
    "data",
    "macro",
    "macro_status.json"
)

AI_FILE = os.path.join(
    BASE_DIR,
    "data",
    "ai",
    "ai_status.json"
)


def load_json(path, default):

    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_ai_status():

    news = load_json(NEWS_FILE, {})
    macro = load_json(MACRO_FILE, {})

    score = 50

    sentiment = news.get(
        "market_sentiment",
        "NEUTRAL"
    )

    if sentiment == "POSITIVE":
        score += 20

    elif sentiment == "NEGATIVE":
        score -= 20

    regime = macro.get(
        "market_regime",
        "NEUTRAL"
    )

    if regime == "RISK_ON":
        score += 20

    elif regime == "RISK_OFF":
        score -= 20

    if score >= 70:
        bias = "BULLISH"

    elif score <= 30:
        bias = "BEARISH"

    else:
        bias = "NEUTRAL"

    if score <= 25:
        permission = "BLOCK"

    else:
        permission = "ALLOW"

    data = {
        "mode": "AI_V1",
        "ai_bias": bias,
        "confidence": score,
        "trade_permission": permission,
        "reason": (
            f"NEWS={sentiment},"
            f"MACRO={regime}"
        )
    }

    os.makedirs(
        os.path.dirname(AI_FILE),
        exist_ok=True
    )

    with open(
        AI_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2
        )

    return data


def load_ai_status():

    return update_ai_status()


if __name__ == "__main__":

    result = update_ai_status()

    print("AI_UPDATE_OK")
    print("BIAS=" + result["ai_bias"])
    print("CONFIDENCE=" + str(result["confidence"]))
    print("PERMISSION=" + result["trade_permission"])