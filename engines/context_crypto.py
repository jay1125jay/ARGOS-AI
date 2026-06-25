import json
import os

BASE_DIR = r"C:\ARGOS_AI"
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_candidate():
    market = load_json(MARKET_FILE, {})
    best = market.get("best", {})

    action = best.get("action", "WAIT")
    score = float(best.get("signal_score", 0) or 0)
    risk_score = float(best.get("risk_score", 100) or 100)

    if action not in ["LONG", "SHORT"]:
        priority = 0
    else:
        priority = 90

    return {
        "market": "CRYPTO",
        "symbol": best.get("symbol", "NONE"),
        "action": action,
        "score": score,
        "risk_score": risk_score,
        "priority": priority,
        "status": "ACTIVE",
        "source": "CRYPTO_SCALP_ENGINE_V15"
    }