import json
import os
from datetime import datetime

from engines.market_router import collect_market_candidates

BASE_DIR = r"C:\ARGOS_AI"

AUTO_DIR = os.path.join(BASE_DIR, "data", "auto")
AUTO_FILE = os.path.join(AUTO_DIR, "auto_status.json")


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def candidate_score(item):
    action = item.get("action", "WAIT")
    score = float(item.get("score", 0) or 0)
    risk = float(item.get("risk_score", 100) or 100)
    status = item.get("status", "PLACEHOLDER")

    if status != "ACTIVE":
        return -999

    if action not in ["LONG", "SHORT"]:
        return -100

    if action == "LONG":
        strength = score
    else:
        strength = 100 - score

    return strength - risk


def select_auto_candidate():
    data = collect_market_candidates()
    candidates = data.get("candidates", [])

    selected = None
    if candidates:
        selected = sorted(candidates, key=candidate_score, reverse=True)[0]

    if not selected or candidate_score(selected) < 0:
        selected = {
            "market": "NONE",
            "symbol": "NONE",
            "action": "WAIT",
            "score": 0,
            "risk_score": 100,
            "status": "NO_VALID_CANDIDATE",
            "source": "AUTO_SELECTOR"
        }

    auto_status = {
        "engine": "ARGOS_AUTO_SELECTOR_V13",
        "mode": "PAPER_ONLY",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "auto_start_ready": True,
        "real_order_enabled": False,
        "api_order_enabled": False,
        "auto_real_order_enabled": False,
        "selected": selected,
        "candidates": candidates
    }

    save_json(AUTO_FILE, auto_status)
    return auto_status


if __name__ == "__main__":
    result = select_auto_candidate()
    print("ARGOS_AUTO_SELECTOR_OK")
    print("ENGINE=" + result["engine"])
    print("SELECTED_MARKET=" + result["selected"]["market"])
    print("SELECTED_SYMBOL=" + result["selected"]["symbol"])
    print("SELECTED_ACTION=" + result["selected"]["action"])