import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_crypto_candidate():
    market = load_json(MARKET_FILE, {})
    best = market.get("best", {})

    return {
        "market": "CRYPTO",
        "symbol": best.get("symbol", "NONE"),
        "action": best.get("action", "WAIT"),
        "score": best.get("signal_score", 0),
        "risk_score": best.get("risk_score", 100),
        "status": "ACTIVE",
        "source": "CRYPTO_SCALP_ENGINE"
    }


def build_placeholder(market_name):
    return {
        "market": market_name,
        "symbol": "NONE",
        "action": "WAIT",
        "score": 0,
        "risk_score": 100,
        "status": "PLACEHOLDER",
        "source": market_name + "_ENGINE_PENDING"
    }


def collect_market_candidates():
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "PAPER_ONLY",
        "candidates": [
            build_crypto_candidate(),
            build_placeholder("KR_STOCK"),
            build_placeholder("US_STOCK"),
            build_placeholder("FUTURES")
        ]
    }