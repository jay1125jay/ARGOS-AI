import json
import os
from datetime import datetime

from engines.order_router import route_order_by_mode
from engines.kill_switch_engine import run_kill_switch
from engines.settings_engine import load_settings

BASE_DIR = r"C:\ARGOS_AI"

DECISION_FILE = os.path.join(BASE_DIR, "data", "decision", "decision_status.json")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_market_price(symbol, market):
    for item in market.get("results", []):
        if item.get("symbol") == symbol:
            return float(item.get("price", 0))
    return 0.0


def build_order_plan(decision, market):
    symbol = decision.get("symbol", "NONE")
    action = decision.get("market_action", "WAIT")
    signal_score = decision.get("signal_score", 0)
    risk_score = decision.get("risk_score", 100)
    price = find_market_price(symbol, market)

    if not decision.get("auto_allowed", False):
        return {
            "symbol": symbol,
            "execution_action": "NO_ORDER",
            "direction": "NONE",
            "entry": 0,
            "tp1": 0,
            "tp2": 0,
            "sl": 0,
            "position_size": 1000.0,
            "max_hold_seconds": 900,
            "market_price": price,
            "market_action": action,
            "signal_score": signal_score,
            "risk_score": risk_score,
            "paper_order_ready": False,
            "reason": "Decision engine did not allow execution."
        }

    if action not in ["LONG", "SHORT"]:
        return {
            "symbol": symbol,
            "execution_action": "NO_ORDER",
            "direction": "NONE",
            "entry": 0,
            "tp1": 0,
            "tp2": 0,
            "sl": 0,
            "position_size": 1000.0,
            "max_hold_seconds": 900,
            "market_price": price,
            "market_action": action,
            "signal_score": signal_score,
            "risk_score": risk_score,
            "paper_order_ready": False,
            "reason": "No executable paper setup."
        }

    entry = price

    if action == "LONG":
        tp1 = round(entry * 1.003, 6)
        tp2 = round(entry * 1.006, 6)
        sl = round(entry * 0.996, 6)
    else:
        tp1 = round(entry * 0.997, 6)
        tp2 = round(entry * 0.994, 6)
        sl = round(entry * 1.004, 6)

    return {
        "symbol": symbol,
        "execution_action": "PAPER_ENTRY_READY",
        "direction": action,
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "position_size": 1000.0,
        "max_hold_seconds": 900,
        "market_price": price,
        "market_action": action,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "paper_order_ready": True,
        "reason": "Execution plan created."
    }


def run_execution_engine():
    settings = load_settings()
    decision = load_json(DECISION_FILE, {})
    market = load_json(MARKET_FILE, {})

    kill_switch = run_kill_switch()
    order_plan = build_order_plan(decision, market)

    if kill_switch.get("blocked"):
        order_plan["execution_action"] = "NO_ORDER"
        order_plan["direction"] = "NONE"
        order_plan["paper_order_ready"] = False
        order_plan["reason"] = "Blocked by kill switch: " + ",".join(kill_switch.get("tags", []))

    execution_mode = settings.get("execution_mode", "PAPER")
    route = route_order_by_mode(order_plan, execution_mode)

    status = {
        "mode": settings.get("system_mode", "PAPER_ONLY"),
        "engine": "ARGOS_EXECUTION_ENGINE_V18_LIVE_READY",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "execution_mode": settings.get("execution_mode", "PAPER"),
        "adapter_engine": route.get("adapter_engine", "-"),
        "route_target": route.get("route_target", "-"),
        "symbol": order_plan.get("symbol", "NONE"),
        "execution_action": order_plan.get("execution_action", "NO_ORDER"),
        "direction": order_plan.get("direction", "NONE"),
        "entry": order_plan.get("entry", 0),
        "tp1": order_plan.get("tp1", 0),
        "tp2": order_plan.get("tp2", 0),
        "sl": order_plan.get("sl", 0),
        "position_size": order_plan.get("position_size", 1000.0),
        "max_hold_seconds": order_plan.get("max_hold_seconds", 900),
        "market_price": order_plan.get("market_price", 0),
        "market_action": order_plan.get("market_action", "WAIT"),
        "signal_score": order_plan.get("signal_score", 0),
        "risk_score": order_plan.get("risk_score", 100),
        "reason": order_plan.get("reason", ""),
        "paper_order_ready": order_plan.get("paper_order_ready", False),
        "real_order_enabled": settings.get("real_order_enabled", False),
        "api_order_enabled": settings.get("api_order_enabled", False),
        "kill_switch_blocked": kill_switch.get("blocked", False),
        "kill_switch_tags": kill_switch.get("tags", []),
        "auto_real_order_enabled": settings.get("auto_real_order_enabled", False),
    }

    save_json(EXECUTION_FILE, status)
    return status

def build_execution_plan():
    return run_execution_engine()

if __name__ == "__main__":
    result = run_execution_engine()
    print("ARGOS_EXECUTION_ENGINE_OK")
    print("ENGINE=" + result["engine"])
    print("EXECUTION_MODE=" + result["execution_mode"])
    print("ADAPTER_ENGINE=" + result["adapter_engine"])
    print("ROUTE_TARGET=" + result["route_target"])
    print("ACTION=" + result["execution_action"])