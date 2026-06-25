def route_order(order_plan):
    return {
        "adapter_engine": "ARGOS_ORDER_ADAPTER_LIVE_V18",
        "route_target": "LIVE",
        "status": "BLOCKED",
        "reason": "LIVE adapter is disabled. Real order execution not allowed.",
        "order_payload": order_plan
    }