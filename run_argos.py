import json
import os
import urllib.request
from datetime import datetime

from engines.portfolio_engine import calculate_portfolio
from engines.position_manager import check_all_exits, load_positions
from engines.technical_engine import build_signal
from engines.report_engine import (
    ensure_report_files,
    save_trade,
    get_latest_report,
    calculate_report,
    save_report,
)
from engines.decision_engine import build_decision
from engines.execution_engine import build_execution_plan
from engines.paper_router import route_paper_order


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
    print("AUTO_REAL_ORDER=FALSE")
    print("-" * 50)

    results, best = scan_market()
    print_market(results)

    print("-" * 50)
    print(f"BEST_SYMBOL={best['symbol']}")
    print(f"BEST_ACTION={best['action']}")
    print(f"BEST_SIGNAL_SCORE={best['signal_score']}")
    print(f"BEST_RISK_SCORE={best['risk_score']}")

    closed_trades = check_all_exits(results)

    for trade in closed_trades:
        save_trade(trade)
        trade_changed = True

        print("POSITION_EXIT=EXECUTED")
        print(f"EXIT_SYMBOL={trade['symbol']}")
        print(f"EXIT_REASON={trade.get('exit_reason')}")
        print(f"PNL={trade['pnl']}")
        print(f"RESULT={trade['result']}")

    decision = build_decision()

    print("-" * 50)
    print("DECISION_ENGINE=OK")
    print("DECISION_SYMBOL=" + str(decision.get("symbol")))
    print("DECISION=" + str(decision.get("decision")))
    print("DECISION_ACTION=" + str(decision.get("action")))
    print("AUTO_ALLOWED=" + str(decision.get("auto_allowed")))

    execution = build_execution_plan()

    print("-" * 50)
    print("EXECUTION_ENGINE=OK")
    print("EXECUTION_ACTION=" + str(execution.get("execution_action")))
    print("EXECUTION_SYMBOL=" + str(execution.get("symbol")))
    print("EXECUTION_DIRECTION=" + str(execution.get("direction")))
    print("PAPER_ORDER_READY=" + str(execution.get("paper_order_ready")))
    print("REAL_ORDER_ENABLED=" + str(execution.get("real_order_enabled")))
    print("API_ORDER_ENABLED=" + str(execution.get("api_order_enabled")))

    router = route_paper_order()

    print("-" * 50)
    print("PAPER_ROUTER=OK")
    print("ROUTER_STATUS=" + str(router.get("status")))
    print("ROUTER_REASON=" + str(router.get("reason")))
    print("ROUTER_REAL_ORDER_ENABLED=" + str(router.get("real_order_enabled")))
    print("ROUTER_API_ORDER_ENABLED=" + str(router.get("api_order_enabled")))
    print("ROUTER_AUTO_REAL_ORDER_ENABLED=" + str(router.get("auto_real_order_enabled")))

    if router.get("status") == "PAPER_POSITION_OPENED":
        trade_changed = True

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