import json
import os

BASE_DIR = r"C:\ARGOS_AI"

CHART_DIR = os.path.join(BASE_DIR, "data", "chart")
CHART_FILE = os.path.join(CHART_DIR, "chart_state.json")


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def map_tradingview_symbol(market, symbol):
    market = market.upper()
    symbol = symbol.upper()

    if market == "CRYPTO":
        return "BINANCE:" + symbol

    if market == "US_STOCK":
        return "NASDAQ:" + symbol

    if market == "KR_STOCK":
        return "KRX:" + symbol

    if market == "FUTURES":
        return "CME_MINI:" + symbol + "1!"

    return symbol


def build_chart_state(market="CRYPTO", symbol="BTCUSDT", interval="5m"):
    display_symbol = map_tradingview_symbol(market, symbol)

    data = {
        "mode": "PAPER_ONLY",
        "market": market,
        "symbol": symbol,
        "interval": interval,
        "provider": "TRADINGVIEW",
        "display_symbol": display_symbol,
        "entry": 0,
        "current": 0,
        "tp": 0,
        "sl": 0,
        "direction": "WAIT"
    }

    save_json(CHART_FILE, data)
    return data


if __name__ == "__main__":
    result = build_chart_state()
    print("ARGOS_CHART_UPDATE_OK")
    print("MARKET=" + result["market"])
    print("SYMBOL=" + result["symbol"])
    print("DISPLAY_SYMBOL=" + result["display_symbol"])