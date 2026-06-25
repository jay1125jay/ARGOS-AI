from engines.order_adapter_paper import route_order as route_paper
from engines.order_adapter_live_ready import route_order as route_live_ready
from engines.order_adapter_live import route_order as route_live


def route_order_by_mode(order_plan, execution_mode):
    mode = str(execution_mode or "PAPER").upper()

    if mode == "PAPER":
        return route_paper(order_plan)

    if mode == "LIVE_READY":
        return route_live_ready(order_plan)

    if mode == "LIVE":
        return route_live(order_plan)

    return {
        "adapter_engine": "ARGOS_ORDER_ROUTER_V18",
        "route_target": "UNKNOWN",
        "status": "BLOCKED",
        "reason": f"Unknown execution mode: {mode}",
        "order_payload": order_plan
    }