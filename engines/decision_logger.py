import csv
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

LOG_FILE = os.path.join(
    BASE_DIR,
    "data",
    "logs",
    "decision_log.csv"
)


def log_decision(
    symbol,
    action,
    signal_score,
    risk_score,
    reason,
    strategy_version
):

    os.makedirs(
        os.path.dirname(LOG_FILE),
        exist_ok=True
    )

    file_exists = os.path.exists(LOG_FILE)

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "time",
                "symbol",
                "action",
                "signal_score",
                "risk_score",
                "reason",
                "strategy_version"
            ])

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            symbol,
            action,
            signal_score,
            risk_score,
            reason,
            strategy_version
        ])
