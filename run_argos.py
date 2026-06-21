import csv
import os
import random
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"
TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]

MODE = "PAPER_ONLY"
REAL_ORDER = False
API_ORDER = False

def ensure_files():
    os.makedirs(os.path.dirname(TRADES_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "symbol", "action", "entry", "exit", "pnl", "result"])

    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "total_trades", "wins", "losses", "win_rate", "total_pnl"])

def generate_signal():
    symbol = random.choice(SYMBOLS)
    signal_score = random.randint(0, 100)
    risk_score = random.randint(0, 100)

    if risk_score > 70:
        action = "WAIT"
    elif signal_score >= 65:
        action = "LONG"
    elif signal_score <= 35:
        action = "SHORT"
    else:
        action = "WAIT"

    return symbol, action, signal_score, risk_score

def paper_trade(symbol, action):
    if action == "WAIT":
        return None

    entry = round(random.uniform(100, 1000), 2)
    move = random.uniform(-0.02, 0.02)

    if action == "LONG":
        exit_price = round(entry * (1 + move), 2)
        pnl = round(exit_price - entry, 2)
    else:
        exit_price = round(entry * (1 - move), 2)
        pnl = round(entry - exit_price, 2)

    result = "WIN" if pnl > 0 else "LOSS"

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "action": action,
        "entry": entry,
        "exit": exit_price,
        "pnl": pnl,
        "result": result,
    }

def save_trade(trade):
    with open(TRADES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            trade["time"],
            trade["symbol"],
            trade["action"],
            trade["entry"],
            trade["exit"],
            trade["pnl"],
            trade["result"],
        ])

def update_report():
    trades = []
    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        trades = list(reader)

    total = len(trades)
    wins = sum(1 for t in trades if t["result"] == "WIN")
    losses = sum(1 for t in trades if t["result"] == "LOSS")
    total_pnl = round(sum(float(t["pnl"]) for t in trades), 2) if trades else 0
    win_rate = round((wins / total) * 100, 2) if total else 0

    with open(REPORT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total,
            wins,
            losses,
            win_rate,
            total_pnl,
        ])

    return total, wins, losses, win_rate, total_pnl

def main():
    ensure_files()

    print("ARGOS AI")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("-" * 40)

    symbol, action, signal_score, risk_score = generate_signal()

    print(f"SYMBOL={symbol}")
    print(f"SIGNAL_SCORE={signal_score}")
    print(f"RISK_SCORE={risk_score}")
    print(f"ACTION={action}")

    trade = paper_trade(symbol, action)

    if trade:
        save_trade(trade)
        print("PAPER_TRADE=EXECUTED")
        print(f"PNL={trade['pnl']}")
        print(f"RESULT={trade['result']}")
    else:
        print("PAPER_TRADE=NO_ORDER")

    total, wins, losses, win_rate, total_pnl = update_report()

    print("-" * 40)
    print(f"TOTAL_TRADES={total}")
    print(f"WINS={wins}")
    print(f"LOSSES={losses}")
    print(f"WIN_RATE={win_rate}%")
    print(f"TOTAL_PNL={total_pnl}")

if __name__ == "__main__":
    main()