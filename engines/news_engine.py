import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

NEWS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "news",
    "news_status.json"
)

def load_news_status():

    if not os.path.exists(NEWS_FILE):
        return {
            "mode": "PLACEHOLDER",
            "market_sentiment": "NEUTRAL",
            "risk_level": "NORMAL",
            "headlines": []
        }

    with open(
        NEWS_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

def update_news_placeholder():

    data = {
        "mode": "PLACEHOLDER",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_sentiment": "NEUTRAL",
        "risk_level": "NORMAL",
        "headlines": []
    }

    with open(
        NEWS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2
        )

    return data
