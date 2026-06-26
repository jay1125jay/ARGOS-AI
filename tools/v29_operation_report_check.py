import json
import os
import sys

BASE_DIR = r"C:\ARGOS_AI"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engines.operation_report_engine import generate_operation_report

REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "operation_report.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    generate_operation_report()
    data = read_json(REPORT_FILE)

    print("ARGOS V29 OPERATION REPORT CHECK")
    print("=" * 60)
    print("REPORT_ENGINE=" + str(data.get("engine", "-")))
    print("SESSION_LOOPS=" + str(data.get("session", {}).get("loops", 0)))
    print("SIGNALS_TOTAL=" + str(data.get("signals", {}).get("total", 0)))
    print("DECISION_BLOCKED=" + str(data.get("decision", {}).get("blocked", 0)))
    print("PAPER_OPENED=" + str(data.get("execution", {}).get("opened", 0)))
    print("PAPER_CLOSED=" + str(data.get("execution", {}).get("closed", 0)))
    print("WIN_RATE=" + str(data.get("performance", {}).get("win_rate", 0)))
    print("TOTAL_PNL=" + str(data.get("performance", {}).get("total_pnl", 0)))
    print("HEALTH=" + str(data.get("health", {}).get("status", "-")))
    print("=" * 60)

    if data.get("engine") == "ARGOS_OPERATION_REPORT_V29":
        print("V29_OPERATION_REPORT=PASS")
    else:
        print("V29_OPERATION_REPORT=CHECK_REQUIRED")


if __name__ == "__main__":
    main()