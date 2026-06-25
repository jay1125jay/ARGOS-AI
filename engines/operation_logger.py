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
LOG_FILE = os.path.join(BASE_DIR, "data", "logs", "operation_log.csv")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ensure_log_file():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    if os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "best_symbol",
            "best_action",
            "best_signal_score",
            "best_risk_score",
            "decision",
            "decision_action",
            "execution_action",
            "router_status",
            "router_reason",
            "open_positions",
            "report_total_trades",
            "report_total_pnl"
        ])


def get_latest_report():
    rows = read_csv(REPORT_FILE)
    if not rows:
        return {
            "total_trades": 0,
            "total_pnl": 0
        }
    r = rows[-1]
    return {
        "total_trades": r.get("total_trades", 0),
        "total_pnl": r.get("total_pnl", 0)
    }


def append_operation_log():
    ensure_log_file()

    market = load_json(MARKET_FILE, {})
    decision = load_json(DECISION_FILE, {})
    execution = load_json(EXECUTION_FILE, {})
    router = load_json(ROUTER_FILE, {})
    positions = load_json(POSITIONS_FILE, {"positions": []})
    report = get_latest_report()

    best = market.get("best", {})

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        best.get("symbol", "NONE"),
        best.get("action", "WAIT"),
        best.get("signal_score", 0),
        best.get("risk_score", 100),
        decision.get("decision", "WAIT"),
        decision.get("action", "NO_TRADE"),
        execution.get("execution_action", "NO_ORDER"),
        router.get("status", "WAIT"),
        router.get("reason", "-"),
        len(positions.get("positions", [])),
        report.get("total_trades", 0),
        report.get("total_pnl", 0),
    ]

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    return {
        "status": "OK",
        "log_file": LOG_FILE
    }