import json
import os
from datetime import datetime

from engines.auto_selector import select_auto_candidate
from engines.decision_engine import build_decision
from engines.execution_engine import build_execution_plan
from engines.paper_router import route_paper_order

BASE_DIR = r"C:\ARGOS_AI"
AUTO_START_FILE = os.path.join(BASE_DIR, "data", "auto", "auto_start_status.json")


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_auto_start():
    auto = select_auto_candidate()
    decision = build_decision()
    execution = build_execution_plan()
    router = route_paper_order()

    status = {
        "engine": "ARGOS_AUTO_START_ENGINE_V21",
        "mode": "PAPER_ONLY",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "auto_selector_engine": auto.get("engine", "-"),
        "decision_engine": decision.get("engine", "-"),
        "execution_engine": execution.get("engine", "-"),
        "router_engine": router.get("engine", "-"),
        "selected_market": auto.get("selected", {}).get("market", "NONE"),
        "selected_symbol": auto.get("selected", {}).get("symbol", "NONE"),
        "selected_action": auto.get("selected", {}).get("action", "WAIT"),
        "decision": decision.get("decision", "-"),
        "decision_action": decision.get("action", "-"),
        "execution_action": execution.get("execution_action", "-"),
        "router_status": router.get("status", "-"),
        "router_reason": router.get("reason", "")
    }

    save_json(AUTO_START_FILE, status)
    return status