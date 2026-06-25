def get_candidate():
    return {
        "market": "FUTURES",
        "symbol": "NONE",
        "action": "WAIT",
        "score": 0,
        "risk_score": 100,
        "priority": 60,
        "status": "SKELETON",
        "source": "FUTURES_CONTEXT_ENGINE_V15",
        "watch_data": [
            "macro_event",
            "interest_rate",
            "dxy",
            "session_flow",
            "index_trend",
            "volatility"
        ]
    }