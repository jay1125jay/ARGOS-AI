import json
import os

BASE_DIR = r"C:\ARGOS_AI"

AI_FILE = os.path.join(
    BASE_DIR,
    "data",
    "ai",
    "ai_status.json"
)

def load_ai_status():

    if not os.path.exists(AI_FILE):
        return {
            "mode": "PLACEHOLDER",
            "ai_bias": "NEUTRAL",
            "confidence": 50,
            "trade_permission": "ALLOW",
            "reason": "NO_AI_MODEL"
        }

    with open(
        AI_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)
