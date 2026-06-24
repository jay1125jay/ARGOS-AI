import json
import os
from datetime import datetime

from engines.position_manager import open_position


BASE_DIR = r"C:\ARGOS_AI"

EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
ROUTER_FILE = os.path.join(BASE_DIR, "data", "execution", "paper_router_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_signal_from_execution(execution):
    direction = execution.get("direction", "NONE")
    symbol = execution.get("symbol", "NONE")
    entry = float(execution.get("entry", 0) or 0)

    return {
        "market": execution.get("market", "CRYPTO"),
        "symbol": symbol,
        "action": direction,
        "price": entry
    }


def route_paper_order():
    execution = load_json(EXECUTION_FILE, {})

    mode = execution.get("mode", "PAPER_ONLY")
    execution_action = execution.get("execution_action", "NO_ORDER")
    paper_order_ready = execution.get("paper_order_ready", False)

    real_order_enabled = execution.get("real_order_enabled", False)
    api_order_enabled = execution.get("api_order_enabled", False)
    auto_real_order_enabled = execution.get("auto_real_order_enabled", False)

    status = "NO_ACTION"
    reason = "No paper order routed."
    opened_position = None

    if mode != "PAPER_ONLY":
        status = "BLOCKED"
        reason = "Blocked because mode is not PAPER_ONLY."

    elif real_order_enabled or api_order_enabled or auto_real_order_enabled:
        status = "BLOCKED"
        reason = "Blocked because real/api order flag is enabled."

    elif not paper_order_ready:
        status = "WAIT"
        reason = "Execution engine has no paper-ready order."

    elif execution_action != "PAPER_ENTRY_READY":
        status = "WAIT"
        reason = "Execution action is not PAPER_ENTRY_READY."

    else:
        signal = build_signal_from_execution(execution)
        opened_position = open_position(signal)

        if opened_position:
            status = "PAPER_POSITION_OPENED"
            reason = "Paper position opened from execution plan."
        else:
            status = "SKIPPED"
            reason = "Position manager rejected entry."

    data = {
        "mode": "PAPER_ONLY",
        "engine": "ARGOS_PAPER_ROUTER_V1",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "reason": reason,
        "source_execution_action": execution_action,
        "paper_order_ready": paper_order_ready,
        "real_order_enabled": False,
        "api_order_enabled": False,
        "auto_real_order_enabled": False,
        "opened_position": opened_position
    }

    save_json(ROUTER_FILE, data)
    return data


if __name__ == "__main__":
    result = route_paper_order()

    print("ARGOS_PAPER_ROUTER_OK")
    print("MODE=" + result["mode"])
    print("ENGINE=" + result["engine"])
    print("STATUS=" + result["status"])
    print("REASON=" + result["reason"])
    print("REAL_ORDER_ENABLED=" + str(result["real_order_enabled"]))
    print("API_ORDER_ENABLED=" + str(result["api_order_enabled"]))
    print("AUTO_REAL_ORDER_ENABLED=" + str(result["auto_real_order_enabled"]))