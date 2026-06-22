import os

BASE_DIR = r"C:\ARGOS_AI"

FILES = [
    r"C:\ARGOS_AI\run_argos.py",
    r"C:\ARGOS_AI\app_server.py",
    r"C:\ARGOS_AI\engines\technical_engine.py",
    r"C:\ARGOS_AI\engines\risk_engine.py",
    r"C:\ARGOS_AI\engines\position_manager.py"
]

def get_health():

    total = len(FILES)

    ok = sum(
        1 for f in FILES
        if os.path.exists(f)
    )

    return {
        "status": "OK" if ok == total else "WARNING",
        "files_ok": ok,
        "files_total": total
    }
