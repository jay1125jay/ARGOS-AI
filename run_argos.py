import json
import os
import urllib.request
from datetime import datetime

from engines.portfolio_engine import calculate_portfolio
from engines.position_manager import open_position, check_all_exits, load_positions
from engines.risk_engine import check_risk
from engines.technical_engine import build_signal
from engines.config_loader import get_strategy_version
from engines.decision_logger import log_decision
from engines.cooldown_engine import set_cooldown, is_cooldown_active
from engines.report_engine import (
    ensure_report_files,
    save_trade,
    get_latest_report,
    calculate_report,
    save_report,
)

BASE_DIR = r"C:\ARGOS_AI"

MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def ensure_files():
    os.makedirs(os.path.dirname(MARKET_FILE), exist_ok=True)
    ensure_report_files()


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
                "symbol": symbol,
                "price": 0,
                "change_pct": 0,
                "rsi": 50,
                "ema9": 0,
                "ema21": 0,
                "trend": "ERROR",
                "volume_ratio": 0,
                "atr_pct": 0,
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
            "mode": "PAPER_ONLY",
            "results": results,
            "best": best,
        }, f, indent=2)

    return results, best


def print_market(results):
    for r in results:
        print(
            f"{r['symbol']} PRICE={r['price']} CHANGE={r['change_pct']}% "
            f"RSI={r['rsi']} EMA9={r['ema9']} EMA21={r['ema21']} "
            f"TREND={r['trend']} VOL={r['volume_ratio']} ATR={r['atr_pct']} "
            f"SIGNAL={r['signal_score']} RISK={r['risk_score']} ACTION={r['action']}"
        )


def print_positions():
    data = load_positions()
    positions = data.get("positions", [])

    print("-" * 50)
    print(f"OPEN_POSITIONS={len(positions)}")

    for p in positions:
        print(
            f"HOLDING {p['symbol']} {p['action']} "
            f"ENTRY={p['entry']} TP={p['tp']} SL={p['sl']}"
        )


def main():
    ensure_files()
    trade_changed = False

    print("ARGOS AI")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("-" * 50)

    results, best = scan_market()
    print_market(results)

    print("-" * 50)
    print(f"BEST_SYMBOL={best['symbol']}")
    print(f"BEST_ACTION={best['action']}")
    print(f"BEST_SIGNAL_SCORE={best['signal_score']}")
    print(f"BEST_RISK_SCORE={best['risk_score']}")

    latest_report = get_latest_report()
    strategy_version = get_strategy_version()

    closed_trades = check_all_exits(results)

    for trade in closed_trades:
        save_trade(trade)
        trade_changed = True

        print("POSITION_EXIT=EXECUTED")
        log_decision(trade['symbol'], trade['action'], 0, 0, 'POSITION_EXIT_' + str(trade.get('exit_reason')), strategy_version)
        print(f"EXIT_SYMBOL={trade['symbol']}")
        print(f"EXIT_REASON={trade.get('exit_reason')}")
        print(f"PNL={trade['pnl']}")
        print(f"RESULT={trade['result']}")
        set_cooldown(trade['symbol'], 5)

    for signal in results:
        if signal["action"] not in ["LONG", "SHORT"]:
            continue

        if is_cooldown_active(signal['symbol']):
            print(f"POSITION_ENTRY=COOLDOWN_BLOCKED {signal['symbol']}")
            log_decision(signal['symbol'], signal['action'], signal['signal_score'], signal['risk_score'], 'COOLDOWN_BLOCKED', strategy_version)
            continue

        risk_result = check_risk(signal, latest_report)

        print(f"ENTRY_CHECK {signal['symbol']} ACTION={signal['action']} RISK_ALLOWED={risk_result['allowed']}")
        log_decision(signal['symbol'], signal['action'], signal['signal_score'], signal['risk_score'], 'ENTRY_CHECK', strategy_version)

        if not risk_result["allowed"]:
            if risk_result["reasons"]:
                print("RISK_REASONS=" + ",".join(risk_result["reasons"]))
            continue

        position = open_position(signal)

        if position:
            trade_changed = True

            print("POSITION_ENTRY=EXECUTED")
            log_decision(position['symbol'], position['action'], signal['signal_score'], signal['risk_score'], 'POSITION_ENTRY_EXECUTED', strategy_version)
            print(f"SYMBOL={position['symbol']}")
            print(f"ACTION={position['action']}")
            print(f"ENTRY={position['entry']}")
            print(f"TP={position['tp']}")
            print(f"SL={position['sl']}")
        else:
            print(f"POSITION_ENTRY=BLOCKED {signal['symbol']}")
            log_decision(signal['symbol'], signal['action'], signal['signal_score'], signal['risk_score'], 'POSITION_ENTRY_BLOCKED', strategy_version)

    report = calculate_report()

    if trade_changed:
        save_report(report)

    total = report["total_trades"]
    wins = report["wins"]
    losses = report["losses"]
    win_rate = report["win_rate"]
    total_pnl = report["total_pnl"]

    portfolio = calculate_portfolio({
        "total_pnl": total_pnl,
        "total_trades": total,
        "win_rate": win_rate,
    })

    print_positions()

    print("-" * 50)
    print(f"TOTAL_TRADES={total}")
    print(f"WINS={wins}")
    print(f"LOSSES={losses}")
    print(f"WIN_RATE={win_rate}%")
    print(f"TOTAL_PNL={total_pnl}")
    print(f"CURRENT_BALANCE={portfolio['current_balance']}")


if __name__ == "__main__":
    main()

