import csv
import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

SESSION_FILE = os.path.join(BASE_DIR, "data", "reports", "paper_session.json")
TRADES_FILE = os.path.join(BASE_DIR, "data", "trades", "paper_trades.csv")


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_trades():
    if not os.path.exists(TRADES_FILE):
        return []

    with open(TRADES_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def default_session():
    return {
        "engine": "ARGOS_PAPER_SESSION_V28",
        "session_id": datetime.now().strftime("ARGOS_SESSION_%Y%m%d_%H%M%S"),
        "started_at": now_text(),
        "last_updated": now_text(),
        "ended_at": "",
        "loops": 0,
        "signals_detected": 0,
        "decision_allowed": 0,
        "decision_blocked": 0,
        "paper_orders": 0,
        "paper_opened": 0,
        "paper_closed": 0,
        "wins": 0,
        "losses": 0,
        "win_rate": 0,
        "total_pnl": 0,
        "current_balance": 10000,
        "block_reason": {},
        "engine_errors": 0
    }


def count_trades():
    trades = read_trades()

    wins = 0
    losses = 0
    total_pnl = 0.0

    for t in trades:
        result = t.get("result", "")
        if result == "WIN":
            wins += 1
        elif result == "LOSS":
            losses += 1

        try:
            total_pnl += float(t.get("pnl", 0) or 0)
        except Exception:
            pass

    total = len(trades)
    win_rate = round((wins / total) * 100, 2) if total else 0

    return {
        "paper_closed": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_pnl": round(total_pnl, 6),
        "current_balance": round(10000 + total_pnl, 6)
    }


def update_block_reasons(session, decision):
    reason = str(decision.get("reason", "") or "")
    if not reason:
        return session

    if decision.get("decision") != "BLOCK":
        return session

    parts = [x.strip() for x in reason.replace("|", ",").split(",") if x.strip()]

    for p in parts:
        session["block_reason"][p] = session["block_reason"].get(p, 0) + 1

    return session


def update_paper_session(market, decision, execution, router):
    session = load_json(SESSION_FILE, default_session())

    session["last_updated"] = now_text()
    session["loops"] = int(session.get("loops", 0)) + 1

    best = market.get("best", {})
    best_action = best.get("action", "WAIT")

    if best_action in ["LONG", "SHORT"]:
        session["signals_detected"] = int(session.get("signals_detected", 0)) + 1

    if decision.get("decision") in ["READY_LONG", "READY_SHORT", "ALLOW"]:
        session["decision_allowed"] = int(session.get("decision_allowed", 0)) + 1

    if decision.get("decision") == "BLOCK":
        session["decision_blocked"] = int(session.get("decision_blocked", 0)) + 1
        session = update_block_reasons(session, decision)

    if execution.get("paper_order_ready") is True:
        session["paper_orders"] = int(session.get("paper_orders", 0)) + 1

    if router.get("status") == "PAPER_POSITION_OPENED":
        session["paper_opened"] = int(session.get("paper_opened", 0)) + 1

    trade_stats = count_trades()
    session.update(trade_stats)

    save_json(SESSION_FILE, session)
    return session


if __name__ == "__main__":
    data = load_json(SESSION_FILE, default_session())
    save_json(SESSION_FILE, data)
    print("ARGOS_PAPER_SESSION_READY")
    print("ENGINE=" + data["engine"])
    print("SESSION_ID=" + data["session_id"])