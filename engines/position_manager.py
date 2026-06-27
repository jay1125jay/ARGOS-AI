import json
import os
from datetime import datetime

from engines.argos_config import MAX_POSITIONS, POSITION_SIZE

BASE_DIR = r"C:\ARGOS_AI"
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")


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
    return any(p.get("symbol") == symbol for p in data.get("positions", []))


def can_open_position(symbol):
    data = load_positions()
    positions = data.get("positions", [])
    if len(positions) >= MAX_POSITIONS:
        return False
    if has_symbol_position(symbol):
        return False
    return True


def calculate_pnl(action, entry, exit_price, position_size):
    if action == "LONG":
        pnl_pct = (exit_price - entry) / entry
    else:
        pnl_pct = (entry - exit_price) / entry
    return round(position_size * pnl_pct, 6)


def open_position(signal):
    symbol = signal["symbol"]
    action = signal["action"]

    if action not in ["LONG", "SHORT"]:
        return None
    if not can_open_position(symbol):
        return None

    entry = float(signal.get("entry", signal.get("price", 0)) or 0)
    if entry <= 0:
        return None

    position_size = float(signal.get("position_size", POSITION_SIZE) or POSITION_SIZE)
    tp1 = float(signal.get("tp1", 0) or 0)
    tp2 = float(signal.get("tp2", 0) or 0)
    sl = float(signal.get("sl", 0) or 0)
    max_hold_seconds = int(signal.get("max_hold_seconds", 900) or 900)

    position = {
        "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "action": action,
        "entry": entry,
        "tp": tp1,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "position_size": position_size,
        "remaining_size": position_size,
        "partial_taken": False,
        "break_even_armed": False,
        "max_hold_seconds": max_hold_seconds,
        "signal_score": signal.get("signal_score", 0),
        "risk_score": signal.get("risk_score", 100),
        "status": "OPEN"
    }

    data = load_positions()
    data["positions"].append(position)
    save_positions(data)
    return position


def position_elapsed_seconds(position):
    opened_at = datetime.strptime(position["opened_at"], "%Y-%m-%d %H:%M:%S")
    return int((datetime.now() - opened_at).total_seconds())


def build_trade(position, exit_price, exit_reason, close_size):
    entry = float(position["entry"])
    action = position["action"]
    pnl = calculate_pnl(action, entry, exit_price, close_size)

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": position["symbol"],
        "action": action,
        "entry": entry,
        "exit": exit_price,
        "pnl": pnl,
        "result": "WIN" if pnl > 0 else "LOSS",
        "exit_reason": exit_reason,
        "position_size": close_size
    }


def check_exit_for_signal(current_signal):
    data = load_positions()
    positions = data.get("positions", [])
    if not positions:
        return []

    symbol = current_signal["symbol"]
    price = float(current_signal["price"] or 0)
    if price <= 0:
        return []

    remaining = []
    closed_trades = []

    for position in positions:
        if position["symbol"] != symbol:
            remaining.append(position)
            continue

        action = position["action"]
        remaining_size = float(position.get("remaining_size", position.get("position_size", POSITION_SIZE)))
        tp1 = float(position.get("tp1", 0))
        tp2 = float(position.get("tp2", 0))
        sl = float(position.get("sl", 0))
        partial_taken = bool(position.get("partial_taken", False))
        break_even_armed = bool(position.get("break_even_armed", False))
        entry = float(position["entry"])

        # TIME STOP
        if position_elapsed_seconds(position) >= int(position.get("max_hold_seconds", 900)):
            closed_trades.append(build_trade(position, price, "TIME_STOP", remaining_size))
            continue

        # TP1
        hit_tp1 = False
        if not partial_taken:
            if action == "LONG" and price >= tp1 > 0:
                hit_tp1 = True
            elif action == "SHORT" and price <= tp1 > 0:
                hit_tp1 = True

            if hit_tp1:
                close_size = round(remaining_size * 0.5, 6)
                closed_trades.append(build_trade(position, price, "TP1", close_size))

                position["remaining_size"] = round(remaining_size - close_size, 6)
                position["partial_taken"] = True
                position["break_even_armed"] = True
                position["sl"] = entry
                remaining.append(position)
                continue

        # TP2
        hit_tp2 = False
        if action == "LONG" and price >= tp2 > 0:
            hit_tp2 = True
        elif action == "SHORT" and price <= tp2 > 0:
            hit_tp2 = True

        if hit_tp2:
            closed_trades.append(build_trade(position, price, "TP2", remaining_size))
            continue

        # SL / BE
        hit_sl = False
        if action == "LONG" and price <= sl:
            hit_sl = True
        elif action == "SHORT" and price >= sl:
            hit_sl = True

        if hit_sl:
            exit_reason = "BREAK_EVEN" if break_even_armed and sl == entry else "SL"
            closed_trades.append(build_trade(position, price, exit_reason, remaining_size))
            continue

        remaining.append(position)

    data["positions"] = remaining
    save_positions(data)
    return closed_trades


def check_all_exits(signals):
    closed = []
    for signal in signals:
        trades = check_exit_for_signal(signal)
        if trades:
            closed.extend(trades)
    return closed