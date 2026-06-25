def get_candidate():
    return {
        "market": "KR_STOCK",
        "symbol": "NONE",
        "action": "WAIT",
        "score": 0,
        "risk_score": 100,
        "status": "SKELETON",
        "source": "KR_STOCK_CONTEXT_ENGINE_V14",
        "watch_data": [
            "disclosure",
            "news_material",
            "theme",
            "trading_value",
            "order_flow"
        ]
    }