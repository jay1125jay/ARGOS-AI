import json
import os
import sys

BASE_DIR = r"C:\ARGOS_AI"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

AUTO_FILE = os.path.join(BASE_DIR, "data", "auto", "auto_status.json")
DECISION_FILE = os.path.join(BASE_DIR, "data", "decision", "decision_status.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
ROUTER_FILE = os.path.join(BASE_DIR, "data", "execution", "paper_router_status.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def exists(path):
    return os.path.exists(path)


def check():
    auto = read_json(AUTO_FILE)
    decision = read_json(DECISION_FILE)
    execution = read_json(EXECUTION_FILE)
    router = read_json(ROUTER_FILE)
    positions = read_json(POSITIONS_FILE)
    market = read_json(MARKET_FILE)

    candidates = auto.get("candidates", [])
    selected = auto.get("selected", {})

    safety_ok = (
        auto.get("real_order_enabled") is False
        and auto.get("api_order_enabled") is False
        and auto.get("auto_real_order_enabled") is False
        and decision.get("real_order_enabled") is False
        and decision.get("api_order_enabled") is False
        and execution.get("real_order_enabled") is False
        and execution.get("api_order_enabled") is False
        and execution.get("auto_real_order_enabled") is False
        and router.get("real_order_enabled") is False
        and router.get("api_order_enabled") is False
        and router.get("auto_real_order_enabled") is False
    )

    market_structure_ok = (
        len(candidates) == 4
        and any(c.get("market") == "CRYPTO" for c in candidates)
        and any(c.get("market") == "KR_STOCK" for c in candidates)
        and any(c.get("market") == "US_STOCK" for c in candidates)
        and any(c.get("market") == "FUTURES" for c in candidates)
    )

    auto_ok = (
        auto.get("auto_start_ready") is True
        and auto.get("engine") == "ARGOS_AUTO_SELECTOR_V15"
        and selected.get("market") is not None
    )

    engine_ok = (
        decision.get("engine") == "ARGOS_DECISION_ENGINE_V10_SCALP"
        and execution.get("engine") == "ARGOS_EXECUTION_ENGINE_V12"
        and router.get("engine") == "ARGOS_PAPER_ROUTER_V2"
    )

    data_ok = (
        exists(AUTO_FILE)
        and exists(DECISION_FILE)
        and exists(EXECUTION_FILE)
        and exists(ROUTER_FILE)
        and exists(POSITIONS_FILE)
        and exists(REPORT_FILE)
        and exists(MARKET_FILE)
    )

    print("ARGOS V17 FULL STRUCTURE CHECK")
    print("=" * 60)
    print("DATA_FILES_OK=" + str(data_ok))
    print("ENGINE_VERSION_OK=" + str(engine_ok))
    print("AUTO_OK=" + str(auto_ok))
    print("FOUR_MARKET_STRUCTURE_OK=" + str(market_structure_ok))
    print("SAFETY_FLAGS_OK=" + str(safety_ok))
    print("-" * 60)
    print("SELECTED_MARKET=" + str(selected.get("market", "NONE")))
    print("SELECTED_SYMBOL=" + str(selected.get("symbol", "NONE")))
    print("SELECTED_ACTION=" + str(selected.get("action", "WAIT")))
    print("OPEN_POSITIONS=" + str(len(positions.get("positions", []))))
    print("MARKET_RESULTS=" + str(len(market.get("results", []))))
    print("=" * 60)

    if data_ok and engine_ok and auto_ok and market_structure_ok and safety_ok:
        print("V17_STRUCTURE=PASS")
    else:
        print("V17_STRUCTURE=CHECK_REQUIRED")


if __name__ == "__main__":
    check()