import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

DECISION_FILE = os.path.join(BASE_DIR, "data", "decision", "decision_status.json")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")

EXECUTION_DIR = os.path.join(BASE_DIR, "data", "execution")
EXECUTION_FILE = os.path.join(EXECUTION_DIR, "execution_status.json")

POSITION_SIZE = 1000.0


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_market_item(market, symbol):
    for item in market.get("results", []):
        if item.get("symbol") == symbol:
            return item

    return {}


def build_execution_plan():
    decision = load_json(DECISION_FILE, {})
    market = load_json(MARKET_FILE, {})
    positions = load_json(POSITIONS_FILE, {})

    mode = "PAPER_ONLY"
    symbol = decision.get("symbol", "NONE")
    action = decision.get("action", "NO_TRADE")
    auto_allowed = decision.get("auto_allowed", False)

    open_positions = positions.get("positions", [])
    market_item = find_market_item(market, symbol)

    price = float(market_item.get("price", 0) or 0)
    signal_score = market_item.get("signal_score", 0)
    risk_score = market_item.get("risk_score", 100)
    market_action = market_item.get("action", "WAIT")

    execution_action = "NO_ORDER"
    direction = "NONE"
    entry = 0
    tp = 0
    sl = 0
    position_size = POSITION_SIZE
    reason = "No executable paper setup."

    if len(open_positions) > 0:
        execution_action = "MANAGE_EXISTING_POSITION"
        reason = "Open position exists. New paper entry is blocked."

    elif auto_allowed and action == "PAPER_LONG" and price > 0:
        execution_action = "PAPER_ENTRY_READY"
        direction = "LONG"
        entry = price
        tp = round(price * 1.006, 6)
        sl = round(price * 0.997, 6)
        reason = "Paper long setup is ready."

    elif auto_allowed and action == "PAPER_SHORT" and price > 0:
        execution_action = "PAPER_ENTRY_READY"
        direction = "SHORT"
        entry = price
        tp = round(price * 0.994, 6)
        sl = round(price * 1.003, 6)
        reason = "Paper short setup is ready."

    data = {
        "mode": mode,
        "engine": "ARGOS_EXECUTION_ENGINE_V2",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "execution_action": execution_action,
        "direction": direction,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "position_size": position_size,
        "market_price": price,
        "market_action": market_action,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "reason": reason,
        "paper_order_ready": execution_action == "PAPER_ENTRY_READY",
        "real_order_enabled": False,
        "api_order_enabled": False,
        "auto_real_order_enabled": False
    }

    save_json(EXECUTION_FILE, data)
    return data


if __name__ == "__main__":
    result = build_execution_plan()
    print("ARGOS_EXECUTION_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("ENGINE=" + result["engine"])
    print("SYMBOL=" + result["symbol"])
    print("ACTION=" + result["execution_action"])
    print("DIRECTION=" + result["direction"])
    print("POSITION_SIZE=" + str(result["position_size"]))
    print("PAPER_ORDER_READY=" + str(result["paper_order_ready"]))
    print("REAL_ORDER_ENABLED=" + str(result["real_order_enabled"]))
    print("API_ORDER_ENABLED=" + str(result["api_order_enabled"]))