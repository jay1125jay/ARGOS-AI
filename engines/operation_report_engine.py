import csv
import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

SESSION_FILE = os.path.join(BASE_DIR, "data", "reports", "paper_session.json")
OP_LOG_FILE = os.path.join(BASE_DIR, "data", "logs", "operation_log.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "operation_report.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def runtime_hours(session):
    try:
        start = datetime.strptime(session.get("started_at"), "%Y-%m-%d %H:%M:%S")
        last = datetime.strptime(session.get("last_updated"), "%Y-%m-%d %H:%M:%S")
        return round((last - start).total_seconds() / 3600, 4)
    except Exception:
        return 0


def count_signals(logs):
    long_count = 0
    short_count = 0
    wait_count = 0

    for row in logs:
        action = row.get("best_action", "WAIT")
        if action == "LONG":
            long_count += 1
        elif action == "SHORT":
            short_count += 1
        else:
            wait_count += 1

    return {
        "total": len(logs),
        "long": long_count,
        "short": short_count,
        "wait": wait_count
    }


def generate_operation_report():
    session = read_json(SESSION_FILE)
    logs = read_csv(OP_LOG_FILE)

    report = {
        "engine": "ARGOS_OPERATION_REPORT_V29",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "session": {
            "session_id": session.get("session_id", "-"),
            "runtime_hours": runtime_hours(session),
            "loops": session.get("loops", 0)
        },

        "signals": count_signals(logs),

        "decision": {
            "allowed": session.get("decision_allowed", 0),
            "blocked": session.get("decision_blocked", 0)
        },

        "execution": {
            "orders": session.get("paper_orders", 0),
            "opened": session.get("paper_opened", 0),
            "closed": session.get("paper_closed", 0)
        },

        "performance": {
            "wins": session.get("wins", 0),
            "losses": session.get("losses", 0),
            "win_rate": session.get("win_rate", 0),
            "total_pnl": session.get("total_pnl", 0),
            "balance": session.get("current_balance", 10000)
        },

        "block_reason": session.get("block_reason", {}),

        "health": {
            "engine_errors": session.get("engine_errors", 0),
            "status": "GOOD" if session.get("engine_errors", 0) == 0 else "CHECK"
        }
    }

    save_json(REPORT_FILE, report)
    return report


if __name__ == "__main__":
    data = generate_operation_report()
    print("ARGOS_OPERATION_REPORT_OK")
    print("ENGINE=" + data["engine"])
    print("LOOPS=" + str(data["session"]["loops"]))
    print("SIGNALS=" + str(data["signals"]["total"]))
    print("PNL=" + str(data["performance"]["total_pnl"]))