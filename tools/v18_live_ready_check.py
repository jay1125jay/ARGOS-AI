import json
import os

BASE_DIR = r"C:\ARGOS_AI"
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = read_json(EXECUTION_FILE)

    print("ARGOS V18 LIVE READY CHECK")
    print("=" * 60)
    print("ENGINE=" + str(data.get("engine", "-")))
    print("EXECUTION_MODE=" + str(data.get("execution_mode", "-")))
    print("ADAPTER_ENGINE=" + str(data.get("adapter_engine", "-")))
    print("ROUTE_TARGET=" + str(data.get("route_target", "-")))
    print("EXECUTION_ACTION=" + str(data.get("execution_action", "-")))
    print("PAPER_ORDER_READY=" + str(data.get("paper_order_ready", False)))
    print("REAL_ORDER_ENABLED=" + str(data.get("real_order_enabled", False)))
    print("API_ORDER_ENABLED=" + str(data.get("api_order_enabled", False)))
    print("=" * 60)

    if (
        data.get("engine") == "ARGOS_EXECUTION_ENGINE_V18_LIVE_READY"
        and data.get("execution_mode") == "PAPER"
        and data.get("route_target") == "PAPER"
        and data.get("real_order_enabled") is False
        and data.get("api_order_enabled") is False
    ):
        print("V18_LIVE_READY=PASS")
    else:
        print("V18_LIVE_READY=CHECK_REQUIRED")


if __name__ == "__main__":
    main()