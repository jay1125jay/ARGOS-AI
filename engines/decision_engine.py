import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

AI_FILE = os.path.join(BASE_DIR, "data", "ai", "ai_status.json")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")
COOLDOWN_FILE = os.path.join(BASE_DIR, "data", "cooldown.json")
CHART_ANALYSIS_FILE = os.path.join(BASE_DIR, "data", "chart", "chart_analysis.json")
NEWS_FILE = os.path.join(BASE_DIR, "data", "news", "news_status.json")
MACRO_FILE = os.path.join(BASE_DIR, "data", "macro", "macro_status.json")

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


def build_data_risk(news, macro):
    news_sentiment = news.get("market_sentiment", "NEUTRAL")
    news_risk = news.get("risk_level", "NORMAL")
    macro_regime = macro.get("market_regime", "NEUTRAL")
    macro_rate_risk = macro.get("rate_risk", "NORMAL")
    macro_event_risk = macro.get("event_risk", "NORMAL")

    reasons = []
    blocked = False
    defensive = False

    if news_risk == "HIGH":
        blocked = True
        reasons.append("NEWS_HIGH_RISK")

    if macro_rate_risk == "HIGH" or macro_event_risk == "HIGH":
        blocked = True
        reasons.append("MACRO_HIGH_RISK")

    if news_risk == "WATCH":
        defensive = True
        reasons.append("NEWS_WATCH")

    if macro_rate_risk == "WATCH" or macro_event_risk == "WATCH":
        defensive = True
        reasons.append("MACRO_WATCH")

    if news_sentiment == "NEGATIVE":
        defensive = True
        reasons.append("NEWS_NEGATIVE")

    if macro_regime == "RISK_OFF":
        defensive = True
        reasons.append("MACRO_RISK_OFF")

    if not reasons:
        reasons.append("DATA_NORMAL")

    return {
        "blocked": blocked,
        "defensive": defensive,
        "reasons": reasons,
        "news_sentiment": news_sentiment,
        "news_risk": news_risk,
        "macro_regime": macro_regime,
        "macro_rate_risk": macro_rate_risk,
        "macro_event_risk": macro_event_risk
    }


def build_decision():
    ai = load_json(AI_FILE, {})
    market = load_json(MARKET_FILE, {})
    positions = load_json(POSITIONS_FILE, {})
    cooldown = load_json(COOLDOWN_FILE, {})
    chart = load_json(CHART_ANALYSIS_FILE, {})
    news = load_json(NEWS_FILE, {})
    macro = load_json(MACRO_FILE, {})

    top = get_top_market_item(market)

    symbol = top.get("symbol", "NONE")
    market_action = top.get("action", "WAIT")
    signal_score = float(top.get("signal_score", 0) or 0)
    risk_score = float(top.get("risk_score", 100) or 100)

    argos_state = ai.get("argos_state", "ANALYZING")
    auto_ready = ai.get("auto_ready", False)
    risk_mode = ai.get("risk_mode", "NORMAL")
    confidence = ai.get("confidence", 0)

    chart_signal = chart.get("signal", "WAIT")
    open_positions = positions.get("positions", [])
    in_cooldown = cooldown.get("active", False)

    data_risk = build_data_risk(news, macro)

    decision = "WAIT"
    action = "NO_TRADE"
    reason = "ARGOS is waiting for valid conditions."
    auto_allowed = False

    if len(open_positions) > 0:
        decision = "MANAGE_POSITION"
        action = "MANAGE"
        reason = "Open position exists. ARGOS should manage position first."

    elif in_cooldown:
        decision = "WAIT"
        action = "NO_TRADE"
        reason = "Cooldown is active."

    elif data_risk["blocked"]:
        decision = "BLOCK"
        action = "NO_TRADE"
        reason = ",".join(data_risk["reasons"])

    elif argos_state == "BLOCKED":
        decision = "BLOCK"
        action = "NO_TRADE"
        reason = "ARGOS state is BLOCKED."

    elif risk_score >= 70:
        decision = "BLOCK"
        action = "NO_TRADE"
        reason = "MARKET_SIGNAL_RISK_HIGH"

    elif data_risk["defensive"] and market_action == "WAIT":
        decision = "WAIT"
        action = "NO_TRADE"
        reason = ",".join(data_risk["reasons"]) + ",MARKET_WAIT"

    elif market_action == "LONG" and signal_score >= 65:
        decision = "READY_LONG"
        action = "PAPER_LONG"
        reason = "DATA_ALLOWED,MARKET_LONG_SIGNAL"
        auto_allowed = True

    elif market_action == "SHORT" and signal_score <= 35:
        decision = "READY_SHORT"
        action = "PAPER_SHORT"
        reason = "DATA_ALLOWED,MARKET_SHORT_SIGNAL"
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

    data = {
        "mode": "PAPER_ONLY",
        "engine": "ARGOS_DECISION_ENGINE_V2_DATA_AWARE",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "argos_state": argos_state,
        "risk_mode": risk_mode,
        "confidence": confidence,
        "market_action": market_action,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "news_sentiment": data_risk["news_sentiment"],
        "news_risk": data_risk["news_risk"],
        "macro_regime": data_risk["macro_regime"],
        "macro_rate_risk": data_risk["macro_rate_risk"],
        "macro_event_risk": data_risk["macro_event_risk"],
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
    print("NEWS_RISK=" + str(result["news_risk"]))
    print("MACRO_EVENT_RISK=" + str(result["macro_event_risk"]))
    print("DECISION=" + result["decision"])
    print("ACTION=" + result["action"])
    print("REASON=" + result["reason"])
    print("AUTO_ALLOWED=" + str(result["auto_allowed"]))
    print("REAL_ORDER_ENABLED=" + str(result["real_order_enabled"]))
    print("API_ORDER_ENABLED=" + str(result["api_order_enabled"]))