import csv
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

from engines.portfolio_engine import calculate_portfolio
from engines.analytics_engine import analyze_trades

ROOT = r"C:\ARGOS_AI"
APP = os.path.join(ROOT, "app")

TRADES = os.path.join(ROOT, "data", "trades", "paper_trades.csv")
REPORT = os.path.join(ROOT, "data", "reports", "report.csv")
MARKET = os.path.join(ROOT, "data", "market", "market_status.json")
POSITIONS = os.path.join(ROOT, "data", "open_positions.json")
NEWS = os.path.join(ROOT, "data", "news", "news_status.json")
MACRO = os.path.join(ROOT, "data", "macro", "macro_status.json")
SYSTEM_LOG = os.path.join(ROOT, "data", "logs", "system_log.csv")
DECISION_LOG = os.path.join(ROOT, "data", "logs", "decision_log.csv")
AI = os.path.join(ROOT, "data", "ai", "ai_status.json")


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


def calculate_unrealized_pnl(action, entry, price, position_size):
    if action == "LONG":
        pnl_pct = (price - entry) / entry
    elif action == "SHORT":
        pnl_pct = (entry - price) / entry
    else:
        pnl_pct = 0

    return round(position_size * pnl_pct, 6)


def enrich_positions(positions, market):
    results = market.get("results", [])
    position_list = positions.get("positions", [])

    for position in position_list:
        symbol = position.get("symbol")
        action = position.get("action")
        entry = float(position.get("entry", 0))
        tp = float(position.get("tp", 0))
        sl = float(position.get("sl", 0))
        position_size = float(position.get("position_size", 1000.0))

        current = None

        for item in results:
            if item.get("symbol") == symbol:
                current = item
                break

        if not current:
            position["current_price"] = "-"
            position["unrealized_pnl"] = "-"
            position["tp_distance_pct"] = "-"
            position["sl_distance_pct"] = "-"
            continue

        price = float(current.get("price", 0))

        if action == "LONG":
            tp_distance = ((tp - price) / price) * 100
            sl_distance = ((price - sl) / price) * 100
        elif action == "SHORT":
            tp_distance = ((price - tp) / price) * 100
            sl_distance = ((sl - price) / price) * 100
        else:
            tp_distance = 0
            sl_distance = 0

        position["current_price"] = round(price, 6)
        position["unrealized_pnl"] = calculate_unrealized_pnl(
            action,
            entry,
            price,
            position_size
        )
        position["tp_distance_pct"] = round(tp_distance, 4)
        position["sl_distance_pct"] = round(sl_distance, 4)

    return positions


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/api/status":

            trades = read_csv(TRADES)
            reports = read_csv(REPORT)
            market = read_json(MARKET)
            positions = read_json(POSITIONS)
            news = read_json(NEWS)
            macro = read_json(MACRO)
            system_logs = read_csv(SYSTEM_LOG)
            decision_logs = read_csv(DECISION_LOG)
            ai = read_json(AI)

            latest_report = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "total_pnl": 0
            }

            if reports:
                r = reports[-1]
                latest_report = {
                    "total_trades": r["total_trades"],
                    "wins": r["wins"],
                    "losses": r["losses"],
                    "win_rate": r["win_rate"],
                    "total_pnl": r["total_pnl"]
                }

            portfolio = calculate_portfolio(latest_report)
            positions = enrich_positions(positions, market)
            analytics = analyze_trades()

            body = json.dumps({
                "report": latest_report,
                "portfolio": portfolio,
                "trades": trades[-50:],
                "market": market,
                "positions": positions,
                "analytics": analytics,
                "news": news,
                "macro": macro,
                "system_logs": system_logs[-20:],
                "decision_logs": decision_logs[-50:],
                "ai": ai
            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        file_name = "index.html"

        if self.path.endswith(".css") or self.path.endswith(".js"):
            file_name = self.path[1:]

        file_path = os.path.join(APP, file_name)

        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            return

        with open(file_path, "rb") as f:
            data = f.read()

        content_type = "text/html"

        if file_name.endswith(".css"):
            content_type = "text/css"

        elif file_name.endswith(".js"):
            content_type = "application/javascript"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(data)


HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()

