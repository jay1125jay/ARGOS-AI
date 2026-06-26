import json
import os

BASE_DIR = r"C:\ARGOS_AI"

AUTO_FILE = os.path.join(BASE_DIR, "data", "auto", "auto_status.json")
AUTO_START_FILE = os.path.join(BASE_DIR, "data", "auto", "auto_start_status.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "data", "config", "settings.json")
KILL_SWITCH_FILE = os.path.join(BASE_DIR, "data", "config", "kill_switch_config.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    auto = read_json(AUTO_FILE)
    auto_start = read_json(AUTO_START_FILE)
    execution = read_json(EXECUTION_FILE)
    settings = read_json(SETTINGS_FILE)
    kill_switch = read_json(KILL_SWITCH_FILE)

    auto_ok = auto.get("engine") == "ARGOS_AUTO_SELECTOR_V15"
    execution_ok = execution.get("engine") == "ARGOS_EXECUTION_ENGINE_V18_LIVE_READY"
    auto_start_ok = auto_start.get("engine") == "ARGOS_AUTO_START_ENGINE_V21"
    mode_ok = (
        settings.get("system_mode") == "PAPER_ONLY"
        and settings.get("execution_mode") == "PAPER"
    )
    kill_ok = settings.get("real_order_enabled") is False and settings.get("api_order_enabled") is False

    print("ARGOS V22 FINAL STRUCTURE CHECK")
    print("=" * 60)
    print("AUTO_SELECTOR_OK=" + str(auto_ok))
    print("EXECUTION_V18_OK=" + str(execution_ok))
    print("AUTO_START_V21_OK=" + str(auto_start_ok))
    print("MODE_CONFIG_OK=" + str(mode_ok))
    print("SAFETY_FLAGS_OK=" + str(kill_ok))
    print("-" * 60)
    print("AUTO_ENGINE=" + str(auto.get("engine", "-")))
    print("AUTO_START_ENGINE=" + str(auto_start.get("engine", "-")))
    print("EXECUTION_ENGINE=" + str(execution.get("engine", "-")))
    print("SYSTEM_MODE=" + str(settings.get("system_mode", "-")))
    print("EXECUTION_MODE=" + str(settings.get("execution_mode", "-")))
    print("=" * 60)

    if auto_ok and execution_ok and auto_start_ok and mode_ok and kill_ok:
        print("V22_FINAL_STRUCTURE=PASS")
    else:
        print("V22_FINAL_STRUCTURE=CHECK_REQUIRED")


if __name__ == "__main__":
    main()