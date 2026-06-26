import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

CONFIG_FILE = os.path.join(BASE_DIR, "data", "config", "kill_switch_config.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_kill_switch():
    config = load_json(CONFIG_FILE, {})
    positions = load_json(POSITIONS_FILE, {"positions": []})
    open_count = len(positions.get("positions", []))

    tags = []
    blocked = False

    if config.get("master_kill_switch", False):
        blocked = True
        tags.append("MASTER_KILL_SWITCH")

    if config.get("emergency_mode", False):
        blocked = True
        tags.append("EMERGENCY_MODE")

    if open_count >= int(config.get("max_open_positions", 3)):
        blocked = True
        tags.append("MAX_OPEN_POSITIONS")

    if config.get("force_paper_only", True):
        tags.append("FORCE_PAPER_ONLY")

    return {
        "engine": "ARGOS_KILL_SWITCH_V19",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "blocked": blocked,
        "tags": tags,
        "open_positions": open_count,
        "max_open_positions": int(config.get("max_open_positions", 3)),
        "force_paper_only": config.get("force_paper_only", True)
    }