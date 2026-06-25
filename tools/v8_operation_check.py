import csv
import json
import os
import sys

BASE_DIR = r"C:\ARGOS_AI"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

LOG_FILE = os.path.join(BASE_DIR, "data", "logs", "operation_log.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
ROUTER_FILE = os.path.join(BASE_DIR, "data", "execution", "paper_router_status.json")


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    logs = read_csv(LOG_FILE)
    reports = read_csv(REPORT_FILE)
    positions = read_json(POSITIONS_FILE)
    execution = read_json(EXECUTION_FILE)
    router = read_json(ROUTER_FILE)

    print("ARGOS V8 OPERATION CHECK")
    print("=" * 50)
    print("LOG_ROWS=" + str(len(logs)))
    print("REPORT_ROWS=" + str(len(reports)))
    print("OPEN_POSITIONS=" + str(len(positions.get("positions", []))))
    print("EXECUTION_ENGINE=" + str(execution.get("engine", "-")))
    print("ROUTER_ENGINE=" + str(router.get("engine", "-")))
    print("LAST_EXECUTION_ACTION=" + str(execution.get("execution_action", "-")))
    print("LAST_ROUTER_STATUS=" + str(router.get("status", "-")))
    print("=" * 50)

    if len(logs) > 0:
        print("V8_OPERATION=READY")
    else:
        print("V8_OPERATION=NO_LOG")


if __name__ == "__main__":
    main()