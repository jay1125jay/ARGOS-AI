DAILY_LOSS_LIMIT = -300.0
MAX_CONSECUTIVE_LOSS = 3


def check_risk(signal, report):

    reasons = []

    total_pnl = float(report.get("total_pnl", 0))
    losses = int(report.get("losses", 0))

    if total_pnl <= DAILY_LOSS_LIMIT:
        reasons.append("DAILY_LOSS_LIMIT_BLOCK")

    if losses >= MAX_CONSECUTIVE_LOSS:
        reasons.append("MAX_CONSECUTIVE_LOSS_BLOCK")

    return {
        "allowed": len(reasons) == 0,
        "reasons": reasons,
        "risk_score": signal.get("risk_score", 50),
        "rsi": signal.get("rsi", 50),
    }