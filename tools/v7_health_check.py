import csv
import json
import os
import sys

BASE_DIR = r"C:\ARGOS_AI"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engines.portfolio_engine import calculate_portfolio
TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")
POSITIONS_FILE = os.path.join(BASE_DIR, "data", "open_positions.json")
EXECUTION_FILE = os.path.join(BASE_DIR, "data", "execution", "execution_status.json")
ROUTER_FILE = os.path.join(BASE_DIR, "data", "execution", "paper_router_status.json")


def read_csv(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def check():
    trades = read_csv(TRADES_FILE)
    reports = read_csv(REPORT_FILE)
    positions = read_json(POSITIONS_FILE)
    execution = read_json(EXECUTION_FILE)
    router = read_json(ROUTER_FILE)

    wins = sum(1 for t in trades if t.get("result") == "WIN")
    losses = sum(1 for t in trades if t.get("result") == "LOSS")
    total_trades = len(trades)
    total_pnl = round(sum(to_float(t.get("pnl")) for t in trades), 6)
    win_rate = round((wins / total_trades) * 100, 2) if total_trades else 0

    calculated_report = {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
    }

    latest_report = reports[-1] if reports else {}

    portfolio = calculate_portfolio(calculated_report)
    open_positions = positions.get("positions", [])

    report_matches = True

    if latest_report:
        report_matches = (
            int(float(latest_report.get("total_trades", 0))) == total_trades
            and int(float(latest_report.get("wins", 0))) == wins
            and int(float(latest_report.get("losses", 0))) == losses
            and round(to_float(latest_report.get("win_rate")), 2) == win_rate
            and round(to_float(latest_report.get("total_pnl")), 6) == total_pnl
        )

    safety_ok = (
        execution.get("real_order_enabled") is False
        and execution.get("api_order_enabled") is False
        and execution.get("auto_real_order_enabled") is False
        and router.get("real_order_enabled") is False
        and router.get("api_order_enabled") is False
        and router.get("auto_real_order_enabled") is False
    )

    print("ARGOS V7 HEALTH CHECK")
    print("=" * 50)
    print("TRADES_TOTAL=" + str(total_trades))
    print("TRADES_WINS=" + str(wins))
    print("TRADES_LOSSES=" + str(losses))
    print("TRADES_WIN_RATE=" + str(win_rate))
    print("TRADES_TOTAL_PNL=" + str(total_pnl))
    print("-" * 50)
    print("REPORT_MATCHES_TRADES=" + str(report_matches))
    print("OPEN_POSITIONS=" + str(len(open_positions)))
    print("PORTFOLIO_BALANCE=" + str(portfolio.get("current_balance")))
    print("-" * 50)
    print("EXECUTION_ENGINE=" + str(execution.get("engine", "-")))
    print("ROUTER_ENGINE=" + str(router.get("engine", "-")))
    print("SAFETY_FLAGS_OK=" + str(safety_ok))
    print("=" * 50)

    if report_matches and safety_ok:
        print("V7_HEALTH=PASS")
    else:
        print("V7_HEALTH=CHECK_REQUIRED")


if __name__ == "__main__":
    check()