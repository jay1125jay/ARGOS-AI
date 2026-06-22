import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

MACRO_FILE = os.path.join(
    BASE_DIR,
    "data",
    "macro",
    "macro_status.json"
)

def load_macro_status():

    if not os.path.exists(MACRO_FILE):
        return {
            "mode": "PLACEHOLDER",
            "market_regime": "NEUTRAL",
            "dxy_status": "UNKNOWN",
            "rate_risk": "NORMAL",
            "event_risk": "NORMAL",
            "events": []
        }

    with open(
        MACRO_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

def update_macro_placeholder():

    data = {
        "mode": "PLACEHOLDER",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_regime": "NEUTRAL",
        "dxy_status": "UNKNOWN",
        "rate_risk": "NORMAL",
        "event_risk": "NORMAL",
        "events": []
    }

    with open(
        MACRO_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2
        )

    return data
