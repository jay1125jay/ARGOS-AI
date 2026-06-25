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


def compute_selection_score(item):
    status = item.get("status", "SKELETON")
    action = item.get("action", "WAIT")
    priority = float(item.get("priority", 0) or 0)
    score = float(item.get("score", 0) or 0)
    risk = float(item.get("risk_score", 100) or 100)

    if status != "ACTIVE":
        return -999

    if action not in ["LONG", "SHORT"]:
        return -100

    if action == "LONG":
        action_strength = score
    else:
        action_strength = 100 - score

    return priority + action_strength - risk


def select_auto_candidate():
    data = collect_market_candidates()
    candidates = data.get("candidates", [])

    scored = []
    for item in candidates:
        row = dict(item)
        row["selection_score"] = compute_selection_score(item)
        scored.append(row)

    scored = sorted(scored, key=lambda x: x["selection_score"], reverse=True)

    selected = scored[0] if scored else None

    if not selected or selected["selection_score"] < 0:
        selected = {
            "market": "NONE",
            "symbol": "NONE",
            "action": "WAIT",
            "score": 0,
            "risk_score": 100,
            "priority": 0,
            "selection_score": -999,
            "status": "NO_VALID_CANDIDATE",
            "source": "AUTO_SELECTOR_V15"
        }

    auto_status = {
        "engine": "ARGOS_AUTO_SELECTOR_V15",
        "mode": "PAPER_ONLY",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "auto_start_ready": True,
        "real_order_enabled": False,
        "api_order_enabled": False,
        "auto_real_order_enabled": False,
        "selected": selected,
        "candidates": scored
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
    print("SELECTION_SCORE=" + str(result["selected"].get("selection_score")))