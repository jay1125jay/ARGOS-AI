from engines.event_filter_engine import classify_event_filter


def build_scalp_context():
    event_filter = classify_event_filter()

    filter_action = event_filter["filter_action"]

    size_multiplier = 1.0
    tp_multiplier = 1.0
    sl_multiplier = 1.0
    allow_entry = True

    if filter_action == "HARD_BLOCK":
        allow_entry = False
        size_multiplier = 0.0

    elif filter_action == "CAUTION":
        allow_entry = True
        size_multiplier = 0.5
        tp_multiplier = 0.9
        sl_multiplier = 0.9

    elif filter_action == "VOL_BOOST":
        allow_entry = True
        size_multiplier = 1.0
        tp_multiplier = 1.15
        sl_multiplier = 1.1

    elif filter_action == "WATCHLIST":
        allow_entry = True
        size_multiplier = 1.0

    return {
        "mode": "SCALP",
        "allow_entry": allow_entry,
        "filter_action": filter_action,
        "size_multiplier": size_multiplier,
        "tp_multiplier": tp_multiplier,
        "sl_multiplier": sl_multiplier,
        "tags": event_filter["tags"],
        "news_sentiment": event_filter["news_sentiment"],
        "news_risk": event_filter["news_risk"],
        "macro_regime": event_filter["macro_regime"],
        "macro_rate_risk": event_filter["macro_rate_risk"],
        "macro_event_risk": event_filter["macro_event_risk"]
    }