import os
import sys
import time
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from run_argos import main as run_argos_main


LOOP_COUNT = 360
SLEEP_SECONDS = 30

RUNNER_LOG = os.path.join(BASE_DIR, "data", "logs", "v9_runner_log.txt")


def log(line):
    os.makedirs(os.path.dirname(RUNNER_LOG), exist_ok=True)

    text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {line}"
    print(text)

    with open(RUNNER_LOG, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def main():
    log("V9_RUNNER_START")
    log(f"LOOP_COUNT={LOOP_COUNT}")
    log(f"SLEEP_SECONDS={SLEEP_SECONDS}")

    for i in range(1, LOOP_COUNT + 1):
        log(f"LOOP_START {i}/{LOOP_COUNT}")

        try:
            run_argos_main()
            log(f"LOOP_OK {i}/{LOOP_COUNT}")
        except Exception as e:
            log(f"LOOP_ERROR {i}/{LOOP_COUNT} {str(e)}")

        if i < LOOP_COUNT:
            time.sleep(SLEEP_SECONDS)

    log("V9_RUNNER_END")


if __name__ == "__main__":
    main()