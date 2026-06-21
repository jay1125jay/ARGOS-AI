import time
from datetime import datetime

import run_argos

MODE = "PAPER_ONLY"
REAL_ORDER = False
API_ORDER = False

PRICE_SCAN_SECONDS = 1
ENTRY_CHECK_SECONDS = 3
SIGNAL_UPDATE_SECONDS = 10
REPORT_SECONDS = 30

last_entry_check = 0
last_signal_update = 0
last_report = 0


def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")


def main():
    global last_entry_check, last_signal_update, last_report

    log("ARGOS AI AUTO LOOP START")
    log("MODE=PAPER_ONLY")
    log("REAL_ORDER=FALSE")
    log("API_ORDER=FALSE")

    while True:
        now = time.time()

        if now - last_signal_update >= SIGNAL_UPDATE_SECONDS:
            log("SIGNAL_UPDATE=RUN")
            last_signal_update = now

        if now - last_entry_check >= ENTRY_CHECK_SECONDS:
            log("ENTRY_EXIT_CHECK=RUN")
            run_argos.main()
            last_entry_check = now

        if now - last_report >= REPORT_SECONDS:
            log("REPORT_UPDATE=ACTIVE")
            last_report = now

        time.sleep(PRICE_SCAN_SECONDS)


if __name__ == "__main__":
    main()