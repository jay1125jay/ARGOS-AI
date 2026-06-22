import json
import os

BASE_DIR = r"C:\ARGOS_AI"

MARKET_FILE = os.path.join(
    BASE_DIR,
    "data",
    "market",
    "market_status.json"
)

REGIME_FILE = os.path.join(
    BASE_DIR,
    "data",
    "market",
    "regime_status.json"
)

def update_regime():

    if not os.path.exists(MARKET_FILE):
        return

    with open(
        MARKET_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        market = json.load(f)

    results = market.get(
        "results",
        []
    )

    bullish = 0
    bearish = 0

    avg_vol = 0

    for r in results:

        trend = r.get(
            "trend",
            "NEUTRAL"
        )

        if trend == "UP":
            bullish += 1

        elif trend == "DOWN":
            bearish += 1

        avg_vol += float(
            r.get(
                "atr_pct",
                0
            )
        )

    count = len(results)

    if count:
        avg_vol /= count

    if bullish >= 3:
        regime = "BULL"

    elif bearish >= 3:
        regime = "BEAR"

    else:
        regime = "SIDEWAYS"

    if avg_vol >= 0.30:
        volatility = "HIGH"

    elif avg_vol >= 0.15:
        volatility = "NORMAL"

    else:
        volatility = "LOW"

    data = {
        "market_regime": regime,
        "volatility": volatility,
        "bullish_symbols": bullish,
        "bearish_symbols": bearish,
        "avg_atr_pct": round(
            avg_vol,
            4
        )
    }

    with open(
        REGIME_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2
        )

    return data

if __name__ == "__main__":

    result = update_regime()

    print("REGIME_UPDATE_OK")
    print(
        "REGIME=" +
        result["market_regime"]
    )

    print(
        "VOLATILITY=" +
        result["volatility"]
    )
