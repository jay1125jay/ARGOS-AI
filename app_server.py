import csv
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

ROOT = r"C:\ARGOS_AI"
APP = os.path.join(ROOT, "app")

TRADES = os.path.join(ROOT, "data", "trades", "paper_trades.csv")
REPORT = os.path.join(ROOT, "data", "reports", "report.csv")


def read_csv(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/api/status":

            trades = read_csv(TRADES)
            reports = read_csv(REPORT)

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

            body = json.dumps({
                "report": latest_report,
                "trades": trades[-50:]
            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        file_name = "index.html"

        if self.path.endswith(".css"):
            file_name = self.path[1:]

        elif self.path.endswith(".js"):
            file_name = self.path[1:]

        file_path = os.path.join(APP, file_name)

        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            return

        with open(file_path, "rb") as f:
            data = f.read()

        if file_name.endswith(".css"):
            content_type = "text/css"

        elif file_name.endswith(".js"):
            content_type = "application/javascript"

        else:
            content_type = "text/html"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(data)


HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()