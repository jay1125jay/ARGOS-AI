import csv
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

LOG_FILE = os.path.join(
    BASE_DIR,
    "data",
    "logs",
    "system_log.csv"
)


def log_error(module, message):

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
                "level",
                "module",
                "message"
            ])

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "ERROR",
            module,
            message
        ])


def log_info(module, message):

    os.makedirs(
        os.path.dirname(LOG_FILE),
        exist_ok=True
    )

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "INFO",
            module,
            message
        ])
