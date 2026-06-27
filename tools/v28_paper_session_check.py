import json
import os

BASE_DIR = r"C:\ARGOS_AI"
SESSION_FILE = os.path.join(BASE_DIR, "data", "reports", "paper_session.json")


def read_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = read_json(SESSION_FILE)

    print("ARGOS V28 PAPER SESSION CHECK")
    print("=" * 60)
    print("SESSION_ENGINE=" + str(data.get("engine", "-")))
    print("SESSION_ID=" + str(data.get("session_id", "-")))
    print("LOOPS=" + str(data.get("loops", 0)))
    print("SIGNALS=" + str(data.get("signals_detected", 0)))
    print("BLOCKED=" + str(data.get("decision_blocked", 0)))
    print("PAPER_ORDERS=" + str(data.get("paper_orders", 0)))
    print("PAPER_OPENED=" + str(data.get("paper_opened", 0)))
    print("PAPER_CLOSED=" + str(data.get("paper_closed", 0)))
    print("WIN_RATE=" + str(data.get("win_rate", 0)))
    print("TOTAL_PNL=" + str(data.get("total_pnl", 0)))
    print("CURRENT_BALANCE=" + str(data.get("current_balance", 0)))
    print("ERRORS=" + str(data.get("engine_errors", 0)))
    print("=" * 60)

    if data.get("engine") == "ARGOS_PAPER_SESSION_V28":
        print("V28_PAPER_SESSION=PASS")
    else:
        print("V28_PAPER_SESSION=CHECK_REQUIRED")


if __name__ == "__main__":
    main() 