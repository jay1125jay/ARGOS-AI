import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")

MAX_POSITIONS = 3
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


def has_symbol_position(symbol):
    data = load_positions()
    positions = data.get("positions", [])
    return any(p.get("symbol") == symbol for p in positions)


def can_open_position(symbol):
    data = load_positions()
    positions = data.get("positions", [])

    if len(positions) >= MAX_POSITIONS:
        return False

    if has_symbol_position(symbol):
        return False

    return True


def build_default_tp_sl(action, entry):
    if action == "LONG":
        tp = round(entry * (1 + TP_PCT), 6)
        sl = round(entry * (1 - SL_PCT), 6)
    else:
        tp = round(entry * (1 - TP_PCT), 6)
        sl = round(entry * (1 + SL_PCT), 6)

    return tp, sl


def open_position(signal):
    symbol = signal["symbol"]
    action = signal["action"]

    if action not in ["LONG", "SHORT"]:
        return None

    if not can_open_position(symbol):
        return None

    data = load_positions()

    entry = float(signal.get("entry", signal.get("price", 0)) or 0)

    if entry <= 0:
        return None

    position_size = float(signal.get("position_size", POSITION_SIZE) or POSITION_SIZE)

    tp = signal.get("tp")
    sl = signal.get("sl")

    if tp is None or sl is None:
        tp, sl = build_default_tp_sl(action, entry)
    else:
        tp = float(tp)
        sl = float(sl)

    position = {
        "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "action": action,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "position_size": position_size,
        "signal_score": signal.get("signal_score", 0),
        "risk_score": signal.get("risk_score", 100),
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

    return round(position_size * pnl_pct, 6)


def check_exit_for_signal(current_signal):
    data = load_positions()
    positions = data.get("positions", [])

    if not positions:
        return None

    symbol = current_signal["symbol"]
    price = float(current_signal["price"])

    if price <= 0:
        return None

    remaining = []
    closed_trade = None

    for position in positions:
        if position["symbol"] != symbol:
            remaining.append(position)
            continue

        action = position["action"]
        exit_reason = None

        if action == "LONG":
            if price >= float(position["tp"]):
                exit_reason = "TP"
            elif price <= float(position["sl"]):
                exit_reason = "SL"

        elif action == "SHORT":
            if price <= float(position["tp"]):
                exit_reason = "TP"
            elif price >= float(position["sl"]):
                exit_reason = "SL"

        if not exit_reason:
            remaining.append(position)
            continue

        entry = float(position["entry"])
        position_size = float(position.get("position_size", POSITION_SIZE))
        pnl = calculate_pnl(action, entry, price, position_size)

        closed_trade = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": position["symbol"],
            "action": action,
            "entry": entry,
            "exit": price,
            "pnl": pnl,
            "result": "WIN" if pnl > 0 else "LOSS",
            "exit_reason": exit_reason,
            "position_size": position_size
        }

    data["positions"] = remaining
    save_positions(data)

    return closed_trade


def check_all_exits(signals):
    closed = []

    for signal in signals:
        trade = check_exit_for_signal(signal)
        if trade:
            closed.append(trade)

    return closed