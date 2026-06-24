import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

NEWS_FILE = os.path.join(BASE_DIR, "data", "news", "news_status.json")
MACRO_FILE = os.path.join(BASE_DIR, "data", "macro", "macro_status.json")
CHART_FILE = os.path.join(BASE_DIR, "data", "chart", "chart_analysis.json")
AI_FILE = os.path.join(BASE_DIR, "data", "ai", "ai_status.json")
DECISION_FILE = os.path.join(BASE_DIR, "data", "decision", "decision_status.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")

BRAIN_DIR = os.path.join(BASE_DIR, "data", "brain")
BRAIN_FILE = os.path.join(BRAIN_DIR, "argos_brain_status.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_argos_brain():
    news = load_json(NEWS_FILE, {})
    macro = load_json(MACRO_FILE, {})
    chart = load_json(CHART_FILE, {})
    ai = load_json(AI_FILE, {})
    decision = load_json(DECISION_FILE, {})
    execution = load_json(EXECUTION_FILE, {})

    data = {
        "engine": "ARGOS_BRAIN_V1",
        "mode": "PAPER_ONLY",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "market_summary": {
            "news_sentiment": news.get("market_sentiment", "UNKNOWN"),
            "news_risk": news.get("risk_level", "UNKNOWN"),
            "macro_regime": macro.get("market_regime", "UNKNOWN"),
            "macro_risk": macro.get("event_risk", "UNKNOWN"),
            "chart_signal": chart.get("signal", "WAIT"),
            "chart_confidence": chart.get("confidence", 0)
        },

        "ai_summary": {
            "argos_state": ai.get("argos_state", "UNKNOWN"),
            "ai_bias": ai.get("ai_bias", "UNKNOWN"),
            "confidence": ai.get("confidence", 0),
            "risk_mode": ai.get("risk_mode", "UNKNOWN"),
            "auto_ready": ai.get("auto_ready", False)
        },

        "decision_summary": {
            "decision": decision.get("decision", "WAIT"),
            "action": decision.get("action", "NO_TRADE"),
            "symbol": decision.get("symbol", "NONE"),
            "auto_allowed": decision.get("auto_allowed", False)
        },

        "execution_summary": {
            "execution_action": execution.get("execution_action", "NO_ORDER"),
            "direction": execution.get("direction", "NONE"),
            "entry": execution.get("entry", 0),
            "tp": execution.get("tp", 0),
            "sl": execution.get("sl", 0),
            "paper_order_ready": execution.get("paper_order_ready", False)
        },

        "safety": {
            "real_order_enabled": False,
            "api_order_enabled": False,
            "auto_real_order_enabled": False
        }
    }

    save_json(BRAIN_FILE, data)
    return data


if __name__ == "__main__":
    result = build_argos_brain()

    print("ARGOS_BRAIN_UPDATE_OK")
    print("ENGINE=" + result["engine"])
    print("MODE=" + result["mode"])
    print("DECISION=" + result["decision_summary"]["decision"])
    print("ACTION=" + result["decision_summary"]["action"])
    print("EXECUTION=" + result["execution_summary"]["execution_action"])
    print("REAL_ORDER_ENABLED=" + str(result["safety"]["real_order_enabled"]))