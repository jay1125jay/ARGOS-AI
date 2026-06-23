import json
import os

BASE_DIR = r"C:\ARGOS_AI"

ANALYSIS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "chart",
    "chart_analysis.json"
)

STATE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "chart",
    "chart_state.json"
)


def load_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def analyze_chart():

    state = load_json(STATE_FILE)

    symbol = state.get("symbol", "BTCUSDT")

    data = {
        "engine": "ARGOS_CHART_BRAIN_V1",
        "symbol": symbol,
        "trend": "NEUTRAL",
        "momentum": "NEUTRAL",
        "structure": "SIDEWAYS",
        "signal": "WAIT",
        "confidence": 50
    }

    save_json(ANALYSIS_FILE, data)

    return data


if __name__ == "__main__":

    result = analyze_chart()

    print("ARGOS_CHART_BRAIN_OK")
    print("SYMBOL=" + result["symbol"])
    print("SIGNAL=" + result["signal"])
    print("CONFIDENCE=" + str(result["confidence"]))