import json
import os

BASE_DIR = r"C:\ARGOS_AI"

SETTINGS_FILE = os.path.join(BASE_DIR, "config", "settings.json")
STRATEGY_FILE = os.path.join(BASE_DIR, "config", "strategy.json")


def load_json(path, default=None):
    if default is None:
        default = {}

    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_settings():
    return load_json(SETTINGS_FILE, {})


def load_strategy():
    return load_json(STRATEGY_FILE, {})


def get_symbols():
    strategy = load_strategy()
    return strategy.get("symbols", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"])


def get_strategy_version():
    strategy = load_strategy()
    return strategy.get("strategy_version", "UNKNOWN")


def get_position_size():
    settings = load_settings()
    return float(settings.get("position_size", 1000))


def get_max_positions():
    settings = load_settings()
    return int(settings.get("max_positions", 3))
