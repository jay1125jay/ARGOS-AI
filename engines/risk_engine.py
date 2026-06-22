import csv
import os

BASE_DIR = r"C:\ARGOS_AI"

TRADES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "trades",
    "paper_trades.csv"
)

DAILY_LOSS_LIMIT = -999999.0
MAX_CONSECUTIVE_LOSS = 5


def get_consecutive_losses():

    if not os.path.exists(TRADES_FILE):
        return 0

    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    if not trades:
        return 0

    count = 0

    for trade in reversed(trades):

        if trade["result"] == "LOSS":
            count += 1
        else:
            break

    return count


def check_risk(signal, report):

    reasons = []

    total_pnl = float(report.get("total_pnl", 0))

    consecutive_losses = get_consecutive_losses()

    if total_pnl <= DAILY_LOSS_LIMIT:
        reasons.append("DAILY_LOSS_LIMIT_BLOCK")

    if consecutive_losses >= MAX_CONSECUTIVE_LOSS:
        reasons.append("MAX_CONSECUTIVE_LOSS_BLOCK")

    return {
        "allowed": len(reasons) == 0,
        "reasons": reasons,
        "risk_score": signal.get("risk_score", 50),
        "rsi": signal.get("rsi", 50),
        "consecutive_losses": consecutive_losses
    }