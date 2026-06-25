from datetime import datetime

from engines.context_crypto import get_candidate as get_crypto_candidate
from engines.context_kr_stock import get_candidate as get_kr_stock_candidate
from engines.context_us_stock import get_candidate as get_us_stock_candidate
from engines.context_futures import get_candidate as get_futures_candidate


def collect_market_candidates():
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "PAPER_ONLY",
        "router": "ARGOS_MARKET_ROUTER_V14",
        "candidates": [
            get_crypto_candidate(),
            get_kr_stock_candidate(),
            get_us_stock_candidate(),
            get_futures_candidate()
        ]
    }