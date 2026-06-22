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


def enrich_positions(positions, market):
    results = market.get("results", [])
    position_list = positions.get("positions", [])

    for position in position_list:
        symbol = position.get("symbol")
        action = position.get("action")
        entry = float(position.get("entry", 0))
        tp = float(position.get("tp", 0))
        sl = float(position.get("sl", 0))

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
            pnl = price - entry
            tp_distance = ((tp - price) / price) * 100
            sl_distance = ((price - sl) / price) * 100
        elif action == "SHORT":
            pnl = entry - price
            tp_distance = ((price - tp) / price) * 100
            sl_distance = ((sl - price) / price) * 100
        else:
            pnl = 0
            tp_distance = 0
            sl_distance = 0

        position["current_price"] = round(price, 6)
        position["unrealized_pnl"] = round(pnl, 6)
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
                "analytics": analytics
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

