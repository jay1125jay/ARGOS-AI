import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

AI_FILE = os.path.join(BASE_DIR, "data", "ai", "ai_status.json")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")
COOLDOWN_FILE = os.path.join(BASE_DIR, "data", "cooldown.json")
CHART_ANALYSIS_FILE = os.path.join(BASE_DIR, "data", "chart", "chart_analysis.json")

DECISION_DIR = os.path.join(BASE_DIR, "data", "decision")
DECISION_FILE = os.path.join(DECISION_DIR, "decision_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_top_symbol(market):
    results = market.get("results", [])

    if not results:
        return "NONE"

    best = results[0]
    return best.get("symbol", "NONE")


def build_decision():
    ai = load_json(AI_FILE, {})
    market = load_json(MARKET_FILE, {})
    positions = load_json(POSITIONS_FILE, {})
    cooldown = load_json(COOLDOWN_FILE, {})
    chart = load_json(CHART_ANALYSIS_FILE, {})

    argos_state = ai.get("argos_state", "ANALYZING")
    auto_ready = ai.get("auto_ready", False)
    risk_mode = ai.get("risk_mode", "NORMAL")
    confidence = ai.get("confidence", 0)
    chart_signal = chart.get("signal", "WAIT")
    chart_confidence = chart.get("confidence", 50)

    open_positions = positions.get("positions", [])
    in_cooldown = cooldown.get("active", False)

    symbol = get_top_symbol(market)

    decision = "WAIT"
    action = "NO_TRADE"
    reason = "ARGOS is waiting for valid conditions."
    auto_allowed = False

    if argos_state == "BLOCKED":
        decision = "BLOCK"
        action = "NO_TRADE"
        reason = "ARGOS state is BLOCKED."
        auto_allowed = False

    elif in_cooldown:
        decision = "WAIT"
        action = "NO_TRADE"
        reason = "Cooldown is active."
        auto_allowed = False

    elif len(open_positions) > 0:
        decision = "MANAGE_POSITION"
        action = "MANAGE"
        reason = "Open position exists. ARGOS should manage position first."
        auto_allowed = False

    elif auto_ready and argos_state == "READY_LONG" and chart_signal in ["LONG", "WAIT"]:
        decision = "READY_LONG"
        action = "PAPER_LONG"
        reason = "ARGOS is ready for a paper long decision."
        auto_allowed = True

    elif auto_ready and argos_state == "READY_SHORT" and chart_signal in ["SHORT", "WAIT"]:
        decision = "READY_SHORT"
        action = "PAPER_SHORT"
        reason = "ARGOS is ready for a paper short decision."
        auto_allowed = True

    data = {
        "mode": "PAPER_ONLY",
        "engine": "ARGOS_DECISION_ENGINE_V1",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "argos_state": argos_state,
        "risk_mode": risk_mode,
        "confidence": confidence,
        "decision": decision,
        "action": action,
        "reason": reason,
        "auto_allowed": auto_allowed,
        "real_order_enabled": False,
        "api_order_enabled": False
    }

    save_json(DECISION_FILE, data)
    return data


if __name__ == "__main__":
    result = build_decision()
    print("ARGOS_DECISION_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("ENGINE=" + result["engine"])
    print("SYMBOL=" + result["symbol"])
    print("DECISION=" + result["decision"])
    print("ACTION=" + result["action"])
    print("AUTO_ALLOWED=" + str(result["auto_allowed"]))
    print("REAL_ORDER_ENABLED=" + str(result["real_order_enabled"]))
    print("API_ORDER_ENABLED=" + str(result["api_order_enabled"]))