import json
import os

BASE_DIR = r"C:\ARGOS_AI"

NEWS_FILE = os.path.join(BASE_DIR, "data", "news", "news_status.json")
MACRO_FILE = os.path.join(BASE_DIR, "data", "macro", "macro_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_event_filter():
    news = load_json(NEWS_FILE, {})
    macro = load_json(MACRO_FILE, {})

    news_sentiment = str(news.get("market_sentiment", "NEUTRAL")).upper()
    news_risk = str(news.get("risk_level", "NORMAL")).upper()

    macro_regime = str(macro.get("market_regime", "NEUTRAL")).upper()
    macro_rate_risk = str(macro.get("rate_risk", "NORMAL")).upper()
    macro_event_risk = str(macro.get("event_risk", "NORMAL")).upper()

    tags = []
    hard_block = False
    caution = False
    watchlist = False
    vol_boost = False

    # Only EXTREME blocks paper entry.
    if macro_event_risk == "EXTREME":
        hard_block = True
        tags.append("MACRO_EVENT_EXTREME")

    # HIGH risks become CAUTION, not BLOCK.
    if macro_event_risk == "HIGH":
        caution = True
        tags.append("MACRO_EVENT_HIGH")

    if news_risk == "HIGH":
        caution = True
        tags.append("NEWS_HIGH")

    if macro_rate_risk == "HIGH":
        caution = True
        tags.append("MACRO_RATE_HIGH")

    if news_risk == "WATCH":
        caution = True
        tags.append("NEWS_WATCH")

    if macro_rate_risk == "WATCH" or macro_event_risk == "WATCH":
        caution = True
        tags.append("MACRO_WATCH")

    if news_sentiment == "NEGATIVE":
        caution = True
        tags.append("NEWS_NEGATIVE")

    if macro_regime == "RISK_OFF":
        caution = True
        tags.append("MACRO_RISK_OFF")

    if news_sentiment == "POSITIVE":
        watchlist = True
        vol_boost = True
        tags.append("NEWS_POSITIVE")

    if macro_regime == "RISK_ON":
        watchlist = True
        tags.append("MACRO_RISK_ON")

    if not tags:
        tags.append("FILTER_NORMAL")

    if hard_block:
        filter_action = "HARD_BLOCK"
    elif caution:
        filter_action = "CAUTION"
    elif watchlist and vol_boost:
        filter_action = "VOL_BOOST"
    elif watchlist:
        filter_action = "WATCHLIST"
    else:
        filter_action = "NORMAL"

    return {
        "filter_action": filter_action,
        "hard_block": hard_block,
        "caution": caution,
        "watchlist": watchlist,
        "vol_boost": vol_boost,
        "tags": tags,
        "news_sentiment": news_sentiment,
        "news_risk": news_risk,
        "macro_regime": macro_regime,
        "macro_rate_risk": macro_rate_risk,
        "macro_event_risk": macro_event_risk
    }