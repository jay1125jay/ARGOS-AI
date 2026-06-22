import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")

POSITION_SIZE = 1000.0

TP_PCT = 0.003
SL_PCT = 0.002


def ensure_position_file():
    os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)

    if not os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({"positions": []}, f, indent=2)


def load_positions():
    ensure_position_file()

    with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_positions(data):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def has_open_position():
    data = load_positions()
    return len(data.get("positions", [])) > 0


def open_position(signal):
    data = load_positions()

    if has_open_position():
        return None

    entry = float(signal["price"])
    action = signal["action"]

    if action == "LONG":
        tp = round(entry * (1 + TP_PCT), 6)
        sl = round(entry * (1 - SL_PCT), 6)
    elif action == "SHORT":
        tp = round(entry * (1 - TP_PCT), 6)
        sl = round(entry * (1 + SL_PCT), 6)
    else:
        return None

    position = {
        "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": signal["symbol"],
        "action": action,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "position_size": POSITION_SIZE,
        "status": "OPEN"
    }

    data["positions"].append(position)
    save_positions(data)

    return position


def calculate_pnl(action, entry, exit_price, position_size):
    if action == "LONG":
        pnl_pct = (exit_price - entry) / entry
    else:
        pnl_pct = (entry - exit_price) / entry

    pnl = position_size * pnl_pct

    return round(pnl, 6)


def check_exit(current_signal):
    data = load_positions()
    positions = data.get("positions", [])

    if not positions:
        return None

    position = positions[0]
    price = float(current_signal["price"])
    action = position["action"]

    exit_reason = None

    if action == "LONG":
        if price >= float(position["tp"]):
            exit_reason = "TP"
        elif price <= float(position["sl"]):
            exit_reason = "SL"

    if action == "SHORT":
        if price <= float(position["tp"]):
            exit_reason = "TP"
        elif price >= float(position["sl"]):
            exit_reason = "SL"

    if not exit_reason:
        return None

    entry = float(position["entry"])
    position_size = float(position.get("position_size", POSITION_SIZE))

    pnl = calculate_pnl(
        action,
        entry,
        price,
        position_size
    )

    closed = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": position["symbol"],
        "action": action,
        "entry": entry,
        "exit": price,
        "pnl": pnl,
        "result": "WIN" if pnl > 0 else "LOSS",
        "exit_reason": exit_reason
    }

    data["positions"] = []
    save_positions(data)

    return closed