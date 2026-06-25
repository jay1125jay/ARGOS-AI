def get_candidate():
    return {
        "market": "US_STOCK",
        "symbol": "NONE",
        "action": "WAIT",
        "score": 0,
        "risk_score": 100,
        "status": "SKELETON",
        "source": "US_STOCK_CONTEXT_ENGINE_V14",
        "watch_data": [
            "earnings",
            "guidance",
            "company_news",
            "premarket",
            "sector_flow",
            "macro"
        ]
    }