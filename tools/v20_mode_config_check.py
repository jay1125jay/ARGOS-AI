import json
import os

BASE_DIR = r"C:\ARGOS_AI"
SETTINGS_FILE = os.path.join(BASE_DIR, "data", "config", "settings.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    settings = read_json(SETTINGS_FILE)
    execution = read_json(EXECUTION_FILE)

    print("ARGOS V20 MODE CONFIG CHECK")
    print("=" * 60)
    print("SYSTEM_MODE=" + str(settings.get("system_mode")))
    print("EXECUTION_MODE=" + str(settings.get("execution_mode")))
    print("AUTO_START_ENABLED=" + str(settings.get("auto_start_enabled")))
    print("REAL_ORDER_ENABLED=" + str(settings.get("real_order_enabled")))
    print("API_ORDER_ENABLED=" + str(settings.get("api_order_enabled")))
    print("AUTO_REAL_ORDER_ENABLED=" + str(settings.get("auto_real_order_enabled")))
    print("-" * 60)
    print("EXECUTION_STATUS_MODE=" + str(execution.get("mode")))
    print("EXECUTION_STATUS_EXECUTION_MODE=" + str(execution.get("execution_mode")))
    print("=" * 60)

    if (
        settings.get("system_mode") == "PAPER_ONLY"
        and settings.get("execution_mode") == "PAPER"
        and execution.get("mode") == "PAPER_ONLY"
        and execution.get("execution_mode") == "PAPER"
        and execution.get("real_order_enabled") is False
        and execution.get("api_order_enabled") is False
    ):
        print("V20_MODE_CONFIG=PASS")
    else:
        print("V20_MODE_CONFIG=CHECK_REQUIRED")


if __name__ == "__main__":
    main() 