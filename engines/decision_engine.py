import json
import os
from datetime import datetime

from engines.scalp_context_engine import build_scalp_context

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


def get_top_market_item(market):
    best = market.get("best", {})
    if best:
        return best

    results = market.get("results", [])
    if results:
        return results[0]

    return {
        "symbol": "NONE",
        "action": "WAIT",
        "signal_score": 0,
        "risk_score": 100
    }


def build_decision():
    ai = load_json(AI_FILE, {})
    market = load_json(MARKET_FILE, {})
    positions = load_json(POSITIONS_FILE, {})
    cooldown = load_json(COOLDOWN_FILE, {})
    chart = load_json(CHART_ANALYSIS_FILE, {})

    top = get_top_market_item(market)
    scalp_context = build_scalp_context()

    symbol = top.get("symbol", "NONE")
    market_action = str(top.get("action", "WAIT")).upper()
    signal_score = float(top.get("signal_score", 0) or 0)
    risk_score = float(top.get("risk_score", 100) or 100)

    argos_state = str(ai.get("argos_state", "ANALYZING")).upper()
    auto_ready = bool(ai.get("auto_ready", False))
    risk_mode = str(ai.get("risk_mode", "NORMAL")).upper()
    confidence = ai.get("confidence", 0)

    chart_signal = str(chart.get("signal", "WAIT")).upper()
    open_positions = positions.get("positions", [])
    in_cooldown = cooldown.get("active", False)

    decision = "WAIT"
    action = "NO_TRADE"
    reason = "ARGOS is waiting for valid scalp conditions."
    auto_allowed = False

    filter_action = scalp_context["filter_action"]
    allow_entry = scalp_context["allow_entry"]
    context_tags = scalp_context["tags"]

    if len(open_positions) > 0:
        decision = "MANAGE_POSITION"
        action = "MANAGE"
        reason = "Open position exists. Manage current position first."

    elif in_cooldown:
        decision = "WAIT"
        action = "NO_TRADE"
        reason = "COOLDOWN_ACTIVE"

    elif filter_action == "HARD_BLOCK" or not allow_entry:
        decision = "BLOCK"
        action = "NO_TRADE"
        reason = ",".join(context_tags)

    elif argos_state == "BLOCKED":
        # 기존 BLOCKED라도 HARD_BLOCK 아니면 완전 차단하지 않고 CAUTION 대기
        decision = "WAIT"
        action = "NO_TRADE"
        reason = "AI_STATE_BLOCKED"

    elif risk_score >= 80:
        decision = "BLOCK"
        action = "NO_TRADE"
        reason = "MARKET_SIGNAL_RISK_TOO_HIGH"

    elif market_action == "LONG" and signal_score >= 65:
        decision = "READY_LONG"
        action = "PAPER_LONG"
        reason = "MARKET_LONG_SIGNAL"
        auto_allowed = True

    elif market_action == "SHORT" and signal_score <= 35:
        decision = "READY_SHORT"
        action = "PAPER_SHORT"
        reason = "MARKET_SHORT_SIGNAL"
        auto_allowed = True

    elif auto_ready and argos_state == "READY_LONG" and chart_signal in ["LONG", "WAIT"]:
        decision = "READY_LONG"
        action = "PAPER_LONG"
        reason = "AI_READY_LONG"
        auto_allowed = True

    elif auto_ready and argos_state == "READY_SHORT" and chart_signal in ["SHORT", "WAIT"]:
        decision = "READY_SHORT"
        action = "PAPER_SHORT"
        reason = "AI_READY_SHORT"
        auto_allowed = True

    else:
        if filter_action == "CAUTION":
            reason = "CAUTION_NO_VALID_SIGNAL"
        elif filter_action == "WATCHLIST":
            reason = "WATCHLIST_NO_VALID_SIGNAL"
        elif filter_action == "VOL_BOOST":
            reason = "VOL_BOOST_NO_VALID_SIGNAL"
        else:
            reason = "NO_VALID_SIGNAL"

    data = {
        "mode": "PAPER_ONLY",
        "engine": "ARGOS_DECISION_ENGINE_V10_SCALP",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "argos_state": argos_state,
        "risk_mode": risk_mode,
        "confidence": confidence,
        "market_action": market_action,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "chart_signal": chart_signal,
        "filter_action": filter_action,
        "context_tags": context_tags,
        "size_multiplier": scalp_context["size_multiplier"],
        "tp_multiplier": scalp_context["tp_multiplier"],
        "sl_multiplier": scalp_context["sl_multiplier"],
        "news_sentiment": scalp_context["news_sentiment"],
        "news_risk": scalp_context["news_risk"],
        "macro_regime": scalp_context["macro_regime"],
        "macro_rate_risk": scalp_context["macro_rate_risk"],
        "macro_event_risk": scalp_context["macro_event_risk"],
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
    print("MARKET_ACTION=" + str(result["market_action"]))
    print("FILTER_ACTION=" + str(result["filter_action"]))
    print("DECISION=" + result["decision"])
    print("ACTION=" + result["action"])
    print("REASON=" + result["reason"])
    print("AUTO_ALLOWED=" + str(result["auto_allowed"]))