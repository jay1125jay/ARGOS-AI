import csv
import json
import os
import urllib.request
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]

MODE = "PAPER_ONLY"
REAL_ORDER = False
API_ORDER = False

SIGNAL_LONG_SCORE = 65
SIGNAL_SHORT_SCORE = 35
RISK_BLOCK_SCORE = 70


def ensure_files():
    os.makedirs(os.path.dirname(TRADES_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(MARKET_FILE), exist_ok=True)

    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "symbol", "action", "entry", "exit", "pnl", "result"])

    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "total_trades", "wins", "losses", "win_rate", "total_pnl"])


def fetch_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=50"

    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    closes = [float(candle[4]) for candle in data]
    volumes = [float(candle[5]) for candle in data]

    return closes, volumes


def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0

    gains = []
    losses = []

    for i in range(-period, 0):
        change = closes[i] - closes[i - 1]
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)


def analyze_symbol(symbol):
    closes, volumes = fetch_klines(symbol)

    last_price = closes[-1]
    prev_price = closes[-2]
    change_pct = round(((last_price - prev_price) / prev_price) * 100, 4)

    rsi = calc_rsi(closes)

    signal_score = 50

    if change_pct > 0:
        signal_score += 10
    if change_pct > 0.3:
        signal_score += 15
    if rsi > 55:
        signal_score += 10
    if rsi > 65:
        signal_score += 15

    if change_pct < 0:
        signal_score -= 10
    if change_pct < -0.3:
        signal_score -= 15
    if rsi < 45:
        signal_score -= 10
    if rsi < 35:
        signal_score -= 15

    signal_score = max(0, min(100, signal_score))

    risk_score = 20

    if abs(change_pct) > 0.8:
        risk_score += 30
    if rsi > 75 or rsi < 25:
        risk_score += 30

    risk_score = max(0, min(100, risk_score))

    if risk_score >= RISK_BLOCK_SCORE:
        action = "WAIT"
    elif signal_score >= SIGNAL_LONG_SCORE:
        action = "LONG"
    elif signal_score <= SIGNAL_SHORT_SCORE:
        action = "SHORT"
    else:
        action = "WAIT"

    return {
        "symbol": symbol,
        "price": last_price,
        "change_pct": change_pct,
        "rsi": rsi,
        "signal_score": signal_score,
        "risk_score": risk_score,
        "action": action,
    }


def scan_market():
    results = []

    for symbol in SYMBOLS:
        try:
            results.append(analyze_symbol(symbol))
        except Exception as e:
            results.append({
                "symbol": symbol,
                "price": 0,
                "change_pct": 0,
                "rsi": 50,
                "signal_score": 0,
                "risk_score": 100,
                "action": "WAIT",
                "error": str(e),
            })

    best = sorted(
        results,
        key=lambda x: abs(x["signal_score"] - 50) - x["risk_score"],
        reverse=True
    )[0]

    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": MODE,
            "results": results,
            "best": best,
        }, f, indent=2)

    return results, best


def paper_trade(signal):
    action = signal["action"]

    if action == "WAIT":
        return None

    entry = float(signal["price"])

    if action == "LONG":
        exit_price = round(entry * 1.003, 6)
        pnl = round(exit_price - entry, 6)
    else:
        exit_price = round(entry * 0.997, 6)
        pnl = round(entry - exit_price, 6)

    result = "WIN" if pnl > 0 else "LOSS"

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": signal["symbol"],
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
    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    total = len(trades)
    wins = sum(1 for t in trades if t["result"] == "WIN")
    losses = sum(1 for t in trades if t["result"] == "LOSS")
    total_pnl = round(sum(float(t["pnl"]) for t in trades), 6) if trades else 0
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
    print("-" * 50)

    results, best = scan_market()

    for r in results:
        print(
            f"{r['symbol']} PRICE={r['price']} CHANGE={r['change_pct']}% "
            f"RSI={r['rsi']} SIGNAL={r['signal_score']} "
            f"RISK={r['risk_score']} ACTION={r['action']}"
        )

    print("-" * 50)
    print(f"BEST_SYMBOL={best['symbol']}")
    print(f"BEST_ACTION={best['action']}")
    print(f"BEST_SIGNAL_SCORE={best['signal_score']}")
    print(f"BEST_RISK_SCORE={best['risk_score']}")

    trade = paper_trade(best)

    if trade:
        save_trade(trade)
        print("PAPER_TRADE=EXECUTED")
        print(f"PNL={trade['pnl']}")
        print(f"RESULT={trade['result']}")
    else:
        print("PAPER_TRADE=NO_ORDER")

    total, wins, losses, win_rate, total_pnl = update_report()

    print("-" * 50)
    print(f"TOTAL_TRADES={total}")
    print(f"WINS={wins}")
    print(f"LOSSES={losses}")
    print(f"WIN_RATE={win_rate}%")
    print(f"TOTAL_PNL={total_pnl}")


if __name__ == "__main__":
    main()