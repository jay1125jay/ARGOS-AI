from engines.risk_engine import check_risk

signal = {
    "risk_score": 20,
    "rsi": 55
}

report = {
    "total_pnl": 10,
    "losses": 0
}

result = check_risk(signal, report)

print(result)