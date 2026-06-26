import json
import os

BASE_DIR = r"C:\ARGOS_AI"
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
CONFIG_FILE = os.path.join(BASE_DIR, "data", "config", "kill_switch_config.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    execution = read_json(EXECUTION_FILE)
    config = read_json(CONFIG_FILE)

    print("ARGOS V19 KILL SWITCH CHECK")
    print("=" * 60)
    print("ENGINE=" + str(execution.get("engine", "-")))
    print("MASTER_KILL_SWITCH=" + str(config.get("master_kill_switch", False)))
    print("EMERGENCY_MODE=" + str(config.get("emergency_mode", False)))
    print("FORCE_PAPER_ONLY=" + str(config.get("force_paper_only", True)))
    print("KILL_SWITCH_BLOCKED=" + str(execution.get("kill_switch_blocked", False)))
    print("KILL_SWITCH_TAGS=" + str(execution.get("kill_switch_tags", [])))
    print("EXECUTION_ACTION=" + str(execution.get("execution_action", "-")))
    print("REAL_ORDER_ENABLED=" + str(execution.get("real_order_enabled", False)))
    print("API_ORDER_ENABLED=" + str(execution.get("api_order_enabled", False)))
    print("=" * 60)

    if (
        execution.get("engine") == "ARGOS_EXECUTION_ENGINE_V18_LIVE_READY"
        and config.get("force_paper_only", True) is True
        and execution.get("real_order_enabled") is False
        and execution.get("api_order_enabled") is False
    ):
        print("V19_KILL_SWITCH=PASS")
    else:
        print("V19_KILL_SWITCH=CHECK_REQUIRED")


if __name__ == "__main__":
    main()