import json
import os
import sys

BASE_DIR = r"C:\ARGOS_AI"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engines.auto_selector import select_auto_candidate

AUTO_FILE = os.path.join(BASE_DIR, "data", "auto", "auto_status.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    select_auto_candidate()
    auto = read_json(AUTO_FILE)

    selected = auto.get("selected", {})
    candidates = auto.get("candidates", [])

    print("ARGOS V13 AUTO CHECK")
    print("=" * 50)
    print("ENGINE=" + str(auto.get("engine", "-")))
    print("AUTO_START_READY=" + str(auto.get("auto_start_ready", False)))
    print("CANDIDATES=" + str(len(candidates)))
    print("SELECTED_MARKET=" + str(selected.get("market", "NONE")))
    print("SELECTED_SYMBOL=" + str(selected.get("symbol", "NONE")))
    print("SELECTED_ACTION=" + str(selected.get("action", "WAIT")))
    print("REAL_ORDER_ENABLED=" + str(auto.get("real_order_enabled", False)))
    print("API_ORDER_ENABLED=" + str(auto.get("api_order_enabled", False)))
    print("=" * 50)

    if auto.get("auto_start_ready") and len(candidates) == 4:
        print("V13_AUTO=PASS")
    else:
        print("V13_AUTO=CHECK_REQUIRED")


if __name__ == "__main__":
    main()