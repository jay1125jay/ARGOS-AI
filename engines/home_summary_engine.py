def build_home_summary(
    portfolio,
    report,
    positions,
    decision,
    execution,
    auto_status
):
    open_positions = positions.get("positions", [])
    active = open_positions[0] if open_positions else {}

    selected = auto_status.get("selected", {})

    auto_market = selected.get("market", "NONE")
    auto_symbol = selected.get("symbol", "NONE")
    auto_action = selected.get("action", "WAIT")

    if active:
        symbol = active.get("symbol", "-")
        side = active.get("action", "WAIT")
        size = active.get("position_size", 0)
        pnl = active.get("unrealized_pnl", 0)
    else:
        symbol = auto_symbol if auto_symbol != "NONE" else decision.get("symbol", "-")
        side = auto_action if auto_action != "WAIT" else decision.get("action", "WAIT")
        size = "-"
        pnl = report.get("total_pnl", 0)

    return {
        "mode": "PAPER_ONLY",
        "symbol": symbol,
        "side": side,
        "size": size,
        "pnl": pnl,
        "balance": portfolio.get("current_balance", 0),
        "win_rate": report.get("win_rate", 0),
        "open_positions": len(open_positions),

        "auto_market": auto_market,
        "auto_symbol": auto_symbol,
        "auto_action": auto_action
    }