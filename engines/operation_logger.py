import csv
import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")
DECISION_FILE = os.path.join(BASE_DIR, "data", "decision", "decision_status.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
ROUTER_FILE = os.path.join(BASE_DIR, "data", "execution", "paper_router_status.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")

LOG_DIR = os.path.join(BASE_DIR, "data", "logs")
LOG_FILE = os.path.join(LOG_DIR, "operation_log.csv")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_report():
    if not os.path.exists(REPORT_FILE):
        return {}

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        if not rows:
            return {}
        return rows[-1]


def append_operation_log():
    os.makedirs(LOG_DIR, exist_ok=True)

    market = load_json(MARKET_FILE, {})
    decision = load_json(DECISION_FILE, {})
    execution = load_json(EXECUTION_FILE, {})
    router = load_json(ROUTER_FILE, {})
    positions = load_json(POSITIONS_FILE, {"positions": []})
    report = read_report()

    best = market.get("best", {})

    row = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "best_symbol": best.get("symbol", "NONE"),
        "best_action": best.get("action", "WAIT"),
        "best_signal_score": best.get("signal_score", 0),
        "best_risk_score": best.get("risk_score", 100),

        "decision": decision.get("decision", "WAIT"),
        "decision_action": decision.get("action", "NO_TRADE"),
        "decision_reason": decision.get("reason", "-"),
        "filter_action": decision.get("filter_action", "-"),
        "context_tags": "|".join(decision.get("context_tags", [])),

        "execution_action": execution.get("execution_action", "NO_ORDER"),
        "router_status": router.get("status", "WAIT"),
        "router_reason": router.get("reason", "-"),

        "open_positions": len(positions.get("positions", [])),
        "report_total_trades": report.get("total_trades", 0),
        "report_total_pnl": report.get("total_pnl", 0)
    }

    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "time",
                "best_symbol",
                "best_action",
                "best_signal_score",
                "best_risk_score",
                "decision",
                "decision_action",
                "decision_reason",
                "filter_action",
                "context_tags",
                "execution_action",
                "router_status",
                "router_reason",
                "open_positions",
                "report_total_trades",
                "report_total_pnl",
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)