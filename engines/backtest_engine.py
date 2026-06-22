import csv
import json
import os

BASE_DIR = r"C:\ARGOS_AI"

TRADES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "trades",
    "paper_trades.csv"
)

BACKTEST_FILE = os.path.join(
    BASE_DIR,
    "data",
    "backtest",
    "backtest_status.json"
)

STRATEGY_FILE = os.path.join(
    BASE_DIR,
    "config",
    "strategy.json"
)


def load_strategy_name():
    if not os.path.exists(STRATEGY_FILE):
        return "UNKNOWN"

    with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("strategy_version", "UNKNOWN")


def update_backtest_status():
    strategy_name = load_strategy_name()

    if not os.path.exists(TRADES_FILE):
        trades = []
    else:
        with open(TRADES_FILE, "r", encoding="utf-8") as f:
            trades = list(csv.DictReader(f))

    total = len(trades)
    wins = [t for t in trades if t.get("result") == "WIN"]
    losses = [t for t in trades if t.get("result") == "LOSS"]

    gross_profit = sum(float(t["pnl"]) for t in wins) if wins else 0
    gross_loss = abs(sum(float(t["pnl"]) for t in losses)) if losses else 0

    win_rate = round((len(wins) / total) * 100, 2) if total else 0
    total_pnl = round(sum(float(t["pnl"]) for t in trades), 6) if trades else 0
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss else 0

    data = {
        "mode": "ACTUAL_FROM_TRADES",
        "strategies": [
            {
                "name": strategy_name,
                "total_trades": total,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "profit_factor": profit_factor
            }
        ]
    }

    os.makedirs(os.path.dirname(BACKTEST_FILE), exist_ok=True)

    with open(BACKTEST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def load_backtest_status():
    return update_backtest_status()


if __name__ == "__main__":
    result = update_backtest_status()
    s = result["strategies"][0]

    print("BACKTEST_UPDATE_OK")
    print("MODE=" + result["mode"])
    print("STRATEGY=" + s["name"])
    print("TRADES=" + str(s["total_trades"]))
    print("WIN_RATE=" + str(s["win_rate"]))
    print("TOTAL_PNL=" + str(s["total_pnl"]))
    print("PROFIT_FACTOR=" + str(s["profit_factor"]))
