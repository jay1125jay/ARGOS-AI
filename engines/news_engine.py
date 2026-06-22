import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

NEWS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "news",
    "news_status.json"
)

NEWS_FEEDS = [
    "https://news.google.com/rss/search?q=bitcoin+crypto+market&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=ethereum+crypto+market&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=binance+crypto&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=fed+interest+rates+bitcoin&hl=en-US&gl=US&ceid=US:en"
]

RISK_KEYWORDS = [
    "crash",
    "hack",
    "lawsuit",
    "sec",
    "ban",
    "liquidation",
    "war",
    "fed",
    "rate hike",
    "inflation"
]

POSITIVE_KEYWORDS = [
    "etf",
    "approval",
    "rally",
    "surge",
    "bullish",
    "adoption",
    "record high"
]


def fetch_feed(url):
    headlines = []

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        for item in root.findall(".//item")[:5]:
            title = item.findtext("title", default="")
            link = item.findtext("link", default="")

            if title:
                headlines.append({
                    "title": title,
                    "link": link
                })

    except Exception as e:
        headlines.append({
            "title": "NEWS_FETCH_ERROR: " + str(e),
            "link": ""
        })

    return headlines


def analyze_news(headlines):
    text = " ".join([h["title"].lower() for h in headlines])

    risk_count = sum(1 for word in RISK_KEYWORDS if word in text)
    positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in text)

    if risk_count >= 3:
        risk_level = "HIGH"
    elif risk_count >= 1:
        risk_level = "WATCH"
    else:
        risk_level = "NORMAL"

    if positive_count > risk_count:
        sentiment = "POSITIVE"
    elif risk_count > positive_count:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"

    return sentiment, risk_level


def update_news_status():
    all_headlines = []

    for feed in NEWS_FEEDS:
        all_headlines.extend(fetch_feed(feed))

    all_headlines = all_headlines[:20]

    sentiment, risk_level = analyze_news(all_headlines)

    data = {
        "mode": "LIVE_RSS",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_sentiment": sentiment,
        "risk_level": risk_level,
        "headlines": all_headlines
    }

    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)

    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def load_news_status():
    if not os.path.exists(NEWS_FILE):
        return update_news_status()

    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    result = update_news_status()
    print("NEWS_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("SENTIMENT=" + result["market_sentiment"])
    print("RISK_LEVEL=" + result["risk_level"])
    print("HEADLINES=" + str(len(result["headlines"])))
