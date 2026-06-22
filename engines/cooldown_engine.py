import json
import os
from datetime import datetime, timedelta

BASE_DIR = r"C:\ARGOS_AI"
COOLDOWN_FILE = os.path.join(BASE_DIR, "data", "cooldown.json")


def ensure_cooldown_file():
    os.makedirs(os.path.dirname(COOLDOWN_FILE), exist_ok=True)

    if not os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)


def load_cooldowns():
    ensure_cooldown_file()

    with open(COOLDOWN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cooldowns(data):
    with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def set_cooldown(symbol, minutes=5):
    data = load_cooldowns()
    until = datetime.now() + timedelta(minutes=minutes)

    data[symbol] = until.strftime("%Y-%m-%d %H:%M:%S")
    save_cooldowns(data)


def is_cooldown_active(symbol):
    data = load_cooldowns()

    if symbol not in data:
        return False

    until = datetime.strptime(data[symbol], "%Y-%m-%d %H:%M:%S")

    if datetime.now() >= until:
        del data[symbol]
        save_cooldowns(data)
        return False

    return True


def get_cooldown_until(symbol):
    data = load_cooldowns()
    return data.get(symbol, "")
