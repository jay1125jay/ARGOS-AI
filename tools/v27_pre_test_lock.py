import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"
LOCK_FILE = os.path.join(BASE_DIR, "data", "reports", "v27_pre_test_lock.txt")


def main():
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)

    content = f"""ARGOS V27 PRE TEST LOCK
==================================================
LOCKED_AT={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
CURRENT_TAG=ARGOS_V26_FINAL_PRODUCT_AUDIT

STRUCTURE_STATUS=LOCKED
ENGINE_TUNING=FORBIDDEN
UI_CHANGES=FORBIDDEN
STRATEGY_CHANGES=FORBIDDEN

NEXT_PHASE=PAPER_TEST_ONLY

CHECKLIST:
1. Git status must be clean
2. Server must run on port 8000
3. START_ARGOS.cmd must run
4. START_ARGOS_UI.cmd must run
5. API /api/status must return home_summary and auto
6. PAPER_ONLY must remain true
7. REAL_ORDER must remain false
8. API_ORDER must remain false
9. AUTO_REAL_ORDER must remain false

ARGOS_PRE_TEST_LOCK=PASS
==================================================
"""

    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(content)


if __name__ == "__main__":
    main()