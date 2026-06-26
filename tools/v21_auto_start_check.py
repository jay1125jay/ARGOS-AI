import json
import os

BASE_DIR = r"C:\ARGOS_AI"
AUTO_START_FILE = os.path.join(BASE_DIR, "data", "auto", "auto_start_status.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = read_json(AUTO_START_FILE)

    print("ARGOS V21 AUTO START CHECK")
    print("=" * 60)
    print("ENGINE=" + str(data.get("engine", "-")))
    print("AUTO_SELECTOR_ENGINE=" + str(data.get("auto_selector_engine", "-")))
    print("DECISION_ENGINE=" + str(data.get("decision_engine", "-")))
    print("EXECUTION_ENGINE=" + str(data.get("execution_engine", "-")))
    print("ROUTER_ENGINE=" + str(data.get("router_engine", "-")))
    print("-" * 60)
    print("SELECTED_MARKET=" + str(data.get("selected_market", "NONE")))
    print("SELECTED_SYMBOL=" + str(data.get("selected_symbol", "NONE")))
    print("SELECTED_ACTION=" + str(data.get("selected_action", "WAIT")))
    print("DECISION=" + str(data.get("decision", "-")))
    print("EXECUTION_ACTION=" + str(data.get("execution_action", "-")))
    print("ROUTER_STATUS=" + str(data.get("router_status", "-")))
    print("=" * 60)

    if data.get("engine") == "ARGOS_AUTO_START_ENGINE_V21":
        print("V21_AUTO_START=PASS")
    else:
        print("V21_AUTO_START=CHECK_REQUIRED")


if __name__ == "__main__":
    main()