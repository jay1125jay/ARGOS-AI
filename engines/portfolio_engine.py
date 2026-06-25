from engines.argos_config import START_BALANCE


def calculate_portfolio(report):
    total_pnl = float(report.get("total_pnl", 0))
    total_trades = int(float(report.get("total_trades", 0)))
    win_rate = float(report.get("win_rate", 0))

    current_balance = round(START_BALANCE + total_pnl, 6)
    total_return_pct = round((total_pnl / START_BALANCE) * 100, 4)

    return {
        "start_balance": START_BALANCE,
        "current_balance": current_balance,
        "total_pnl": total_pnl,
        "total_return_pct": total_return_pct,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "open_positions": 0,
    }