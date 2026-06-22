import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

MACRO_FILE = os.path.join(
    BASE_DIR,
    "data",
    "macro",
    "macro_status.json"
)

MACRO_FEEDS = [
    "https://news.google.com/rss/search?q=Federal+Reserve+interest+rates&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=US+CPI+inflation+market&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=DXY+dollar+index+market&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=FOMC+bitcoin+market&hl=en-US&gl=US&ceid=US:en"
]

HIGH_RISK_WORDS = [
    "rate hike",
    "inflation",
    "hot cpi",
    "recession",
    "hawkish",
    "fomc",
    "fed warns"
]

POSITIVE_WORDS = [
    "rate cut",
    "cooling inflation",
    "dovish",
    "soft landing",
    "easing"
]


def fetch_feed(url):
    items = []

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        for item in root.findall(".//item")[:5]:
            title = item.findtext("title", default="")
            link = item.findtext("link", default="")

            if title:
                items.append({
                    "title": title,
                    "link": link
                })

    except Exception as e:
        items.append({
            "title": "MACRO_FETCH_ERROR: " + str(e),
            "link": ""
        })

    return items


def analyze_macro(events):
    text = " ".join([e["title"].lower() for e in events])

    high_count = sum(1 for word in HIGH_RISK_WORDS if word in text)
    positive_count = sum(1 for word in POSITIVE_WORDS if word in text)

    if high_count >= 2:
        event_risk = "HIGH"
        rate_risk = "HIGH"
    elif high_count == 1:
        event_risk = "WATCH"
        rate_risk = "WATCH"
    else:
        event_risk = "NORMAL"
        rate_risk = "NORMAL"

    if positive_count > high_count:
        market_regime = "RISK_ON"
    elif high_count > positive_count:
        market_regime = "RISK_OFF"
    else:
        market_regime = "NEUTRAL"

    return market_regime, rate_risk, event_risk


def update_macro_status():
    events = []

    for feed in MACRO_FEEDS:
        events.extend(fetch_feed(feed))

    events = events[:20]

    market_regime, rate_risk, event_risk = analyze_macro(events)

    data = {
        "mode": "LIVE_RSS",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_regime": market_regime,
        "dxy_status": "RSS_ONLY",
        "rate_risk": rate_risk,
        "event_risk": event_risk,
        "events": events
    }

    os.makedirs(os.path.dirname(MACRO_FILE), exist_ok=True)

    with open(MACRO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def load_macro_status():
    if not os.path.exists(MACRO_FILE):
        return update_macro_status()

    with open(MACRO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    result = update_macro_status()
    print("MACRO_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("REGIME=" + result["market_regime"])
    print("RATE_RISK=" + result["rate_risk"])
    print("EVENT_RISK=" + result["event_risk"])
    print("EVENTS=" + str(len(result["events"])))
