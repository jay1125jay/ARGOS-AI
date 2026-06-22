import csv
import os

BASE_DIR = r"C:\ARGOS_AI"
TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")


def safe_div(a, b):
    return round((a / b) * 100, 2) if b else 0


def analyze_trades():

    if not os.path.exists(TRADES_FILE):
        return {}

    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    if not trades:
        return {}

    total = len(trades)

    wins = [t for t in trades if t["result"] == "WIN"]
    losses = [t for t in trades if t["result"] == "LOSS"]

    long_trades = [t for t in trades if t["action"] == "LONG"]
    short_trades = [t for t in trades if t["action"] == "SHORT"]

    long_wins = [t for t in long_trades if t["result"] == "WIN"]
    short_wins = [t for t in short_trades if t["result"] == "WIN"]

    gross_profit = sum(float(t["pnl"]) for t in wins)
    gross_loss = abs(sum(float(t["pnl"]) for t in losses))

    avg_win = gross_profit / len(wins) if wins else 0
    avg_loss = gross_loss / len(losses) if losses else 0

    symbols = {}

    for t in trades:

        symbol = t["symbol"]

        if symbol not in symbols:
            symbols[symbol] = {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "pnl": 0
            }

        symbols[symbol]["total"] += 1
        symbols[symbol]["pnl"] += float(t["pnl"])

        if t["result"] == "WIN":
            symbols[symbol]["wins"] += 1
        else:
            symbols[symbol]["losses"] += 1

    for symbol in symbols:

        s = symbols[symbol]

        s["win_rate"] = safe_div(
            s["wins"],
            s["total"]
        )

        s["pnl"] = round(
            s["pnl"],
            2
        )

    return {
        "total_trades": total,
        "win_rate": safe_div(len(wins), total),

        "long_win_rate": safe_div(
            len(long_wins),
            len(long_trades)
        ),

        "short_win_rate": safe_div(
            len(short_wins),
            len(short_trades)
        ),

        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),

        "profit_factor": round(
            gross_profit / gross_loss,
            2
        ) if gross_loss else 0,

        "symbols": symbols
    }