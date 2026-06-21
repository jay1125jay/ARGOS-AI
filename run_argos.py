import csv
import json
import os
import urllib.request
from datetime import datetime

from engines.portfolio_engine import calculate_portfolio
from engines.position_manager import open_position, check_exit, load_positions
from engines.risk_engine import check_risk
from engines.technical_engine import build_signal

BASE_DIR = r"C:\ARGOS_AI"

TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "reports", "report.csv")
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def ensure_files():
    os.makedirs(os.path.dirname(TRADES_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(MARKET_FILE), exist_ok=True)


def analyze_symbol(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
    with urllib.request.urlopen(url, timeout=10) as response:
        candles = json.loads(response.read().decode("utf-8"))
    return build_signal(symbol, candles)


def scan_market():
    results = []
    for symbol in SYMBOLS:
        try:
            results.append(analyze_symbol(symbol))
        except Exception as e:
            results.append({
                "symbol": symbol, "price": 0, "change_pct": 0, "rsi": 50,
                "ema9": 0, "ema21": 0, "trend": "ERROR",
                "volume_ratio": 0, "atr_pct": 0,
                "signal_score": 0, "risk_score": 100,
                "action": "WAIT", "error": str(e),
            })

    best = sorted(results, key=lambda x: abs(x["signal_score"] - 50) - x["risk_score"], reverse=True)[0]

    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "PAPER_ONLY",
            "results": results,
            "best": best,
        }, f, indent=2)

    return results, best


def save_trade(trade):
    with open(TRADES_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            trade["time"], trade["symbol"], trade["action"],
            trade["entry"], trade["exit"], trade["pnl"], trade["result"]
        ])


def get_latest_report():
    if not os.path.exists(REPORT_FILE):
        return {"total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0}

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return {"total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0}

    return rows[-1]


def calculate_report():
    if not os.path.exists(TRADES_FILE):
        return 0, 0, 0, 0, 0

    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        trades = list(csv.DictReader(f))

    total = len(trades)
    wins = sum(1 for t in trades if t["result"] == "WIN")
    losses = sum(1 for t in trades if t["result"] == "LOSS")
    total_pnl = round(sum(float(t["pnl"]) for t in trades), 6) if trades else 0
    win_rate = round((wins / total) * 100, 2) if total else 0
    return total, wins, losses, win_rate, total_pnl


def save_report(total, wins, losses, win_rate, total_pnl):
    with open(REPORT_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total, wins, losses, win_rate, total_pnl
        ])


def get_exit_signal(results):
    positions_data = load_positions()
    open_positions = positions_data.get("positions", [])

    if not open_positions:
        return None

    symbol = open_positions[0]["symbol"]

    for signal in results:
        if signal["symbol"] == symbol:
            return signal

    return None


def main():
    ensure_files()
    trade_changed = False

    print("ARGOS AI")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("-" * 50)

    results, best = scan_market()

    for r in results:
        print(
            f"{r['symbol']} PRICE={r['price']} CHANGE={r['change_pct']}% "
            f"RSI={r['rsi']} EMA9={r['ema9']} EMA21={r['ema21']} "
            f"TREND={r['trend']} VOL={r['volume_ratio']} ATR={r['atr_pct']} "
            f"SIGNAL={r['signal_score']} RISK={r['risk_score']} ACTION={r['action']}"
        )

    print("-" * 50)
    print(f"BEST_SYMBOL={best['symbol']}")
    print(f"BEST_ACTION={best['action']}")
    print(f"BEST_SIGNAL_SCORE={best['signal_score']}")
    print(f"BEST_RISK_SCORE={best['risk_score']}")

    latest_report = get_latest_report()

    exit_signal = get_exit_signal(results)
    exit_trade = check_exit(exit_signal) if exit_signal else None

    if exit_trade:
        save_trade(exit_trade)
        trade_changed = True
        print("POSITION_EXIT=EXECUTED")
        print(f"EXIT_SYMBOL={exit_trade['symbol']}")
        print(f"EXIT_REASON={exit_trade.get('exit_reason')}")
        print(f"PNL={exit_trade['pnl']}")
        print(f"RESULT={exit_trade['result']}")
    else:
        risk_result = check_risk(best, latest_report)
        print(f"RISK_ALLOWED={risk_result['allowed']}")

        if risk_result["reasons"]:
            print("RISK_REASONS=" + ",".join(risk_result["reasons"]))

        if risk_result["allowed"]:
            position = open_position(best)

            if position:
                trade_changed = True
                print("POSITION_ENTRY=EXECUTED")
                print(f"SYMBOL={position['symbol']}")
                print(f"ACTION={position['action']}")
                print(f"ENTRY={position['entry']}")
                print(f"TP={position['tp']}")
                print(f"SL={position['sl']}")
            else:
                print("POSITION_ENTRY=BLOCKED_OR_HOLDING")
        else:
            print("POSITION_ENTRY=RISK_BLOCKED")

    total, wins, losses, win_rate, total_pnl = calculate_report()

    if trade_changed:
        save_report(total, wins, losses, win_rate, total_pnl)

    portfolio = calculate_portfolio({
        "total_pnl": total_pnl,
        "total_trades": total,
        "win_rate": win_rate,
    })

    print("-" * 50)
    print(f"TOTAL_TRADES={total}")
    print(f"WINS={wins}")
    print(f"LOSSES={losses}")
    print(f"WIN_RATE={win_rate}%")
    print(f"TOTAL_PNL={total_pnl}")
    print(f"CURRENT_BALANCE={portfolio['current_balance']}")


if __name__ == "__main__":
    main()