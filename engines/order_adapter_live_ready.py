def route_order(order_plan):
    return {
        "adapter_engine": "ARGOS_ORDER_ADAPTER_LIVE_READY_V18",
        "route_target": "LIVE_READY",
        "status": "BLOCKED",
        "reason": "LIVE_READY adapter is structure-only. Real execution disabled.",
        "order_payload": order_plan
    }