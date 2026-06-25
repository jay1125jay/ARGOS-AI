def route_order(order_plan):
    return {
        "adapter_engine": "ARGOS_ORDER_ADAPTER_PAPER_V18",
        "route_target": "PAPER",
        "status": "READY",
        "order_payload": order_plan
    }