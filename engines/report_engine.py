import csv
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")


def ensure_report_files():
    os.makedirs(os.path.dirname(TRADES_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "time",
                "symbol",
                "action",
                "entry",
                "exit",
                "pnl",
                "result"
            ])

    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "time",
                "total_trades",
                "wins",
                "losses",
                "win_rate",
                "total_pnl"
            ])


def save_trade(trade):
    ensure_report_files()

    with open(TRADES_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            trade["time"],
            trade["symbol"],
            trade["action"],
            trade["entry"],
            trade["exit"],
            trade["pnl"],
            trade["result"],
        ])


def get_latest_report():
    ensure_report_files()

    default = {
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0,
        "total_pnl": 0,
    }

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return default

    return rows[-1]


def calculate_report():
    ensure_report_files()

    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    total = len(trades)
    wins = sum(1 for t in trades if t["result"] == "WIN")
    losses = sum(1 for t in trades if t["result"] == "LOSS")
    total_pnl = round(sum(float(t["pnl"]) for t in trades), 6) if trades else 0
    win_rate = round((wins / total) * 100, 2) if total else 0

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
    }


def save_report(report):
    ensure_report_files()

    with open(REPORT_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            report["total_trades"],
            report["wins"],
            report["losses"],
            report["win_rate"],
            report["total_pnl"],
        ])