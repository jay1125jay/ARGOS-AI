import os

BASE_DIR = r"C:\ARGOS_AI"

FILES = [
    os.path.join(BASE_DIR, "run_argos.py"),
    os.path.join(BASE_DIR, "app_server.py"),
    os.path.join(BASE_DIR, "START_ARGOS.cmd"),
    os.path.join(BASE_DIR, "START_ARGOS_UI.cmd"),
    os.path.join(BASE_DIR, "data", "config", "settings.json"),
    os.path.join(BASE_DIR, "data", "config", "kill_switch_config.json"),
    os.path.join(BASE_DIR, "data", "auto", "auto_status.json"),
    os.path.join(BASE_DIR, "data", "auto", "auto_start_status.json"),
    os.path.join(BASE_DIR, "data", "execution", "execution_status.json"),
]


def main():
    print("ARGOS V23 PACKAGE CHECK")
    print("=" * 60)

    missing = []
    for path in FILES:
        ok = os.path.exists(path)
        print(f"{os.path.basename(path)}={ok}")
        if not ok:
            missing.append(path)

    print("=" * 60)
    if missing:
        print("V23_PACKAGE=CHECK_REQUIRED")
        print("MISSING_FILES:")
        for item in missing:
            print(item)
    else:
        print("V23_PACKAGE=PASS")


if __name__ == "__main__":
    main()