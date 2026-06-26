import json
import os

BASE_DIR = r"C:\ARGOS_AI"
SETTINGS_FILE = os.path.join(BASE_DIR, "data", "config", "settings.json")

DEFAULT_SETTINGS = {
    "system_mode": "PAPER_ONLY",
    "execution_mode": "PAPER",
    "auto_start_enabled": True,
    "real_order_enabled": False,
    "api_order_enabled": False,
    "auto_real_order_enabled": False
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = DEFAULT_SETTINGS.copy()
    result.update(data)
    return result