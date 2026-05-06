import logging
from .tools import TOOLS, TOOL_REGISTRY, simulate_impact

logger = logging.getLogger(__name__)

def dispatch_tool(tool_name: str, args: dict):
    canonical = TOOL_REGISTRY.get(tool_name.lower(), tool_name)

    if canonical == "execute_mitigation":
        args.setdefault("action", tool_name)

    if canonical in TOOLS:
        return TOOLS[canonical](**args)

    return {"error": f"{canonical} not found"}


class Boardroom:
    def __init__(self, anomaly_event):
        self.blackboard = {
            "telemetry": anomaly_event,
            "simulations": [],
            "causal_chain": []
        }

    def add_simulation(self, node, result):
        self.blackboard["simulations"].append(result)

        if "affected_nodes" in result:
            self.blackboard["causal_chain"].append({
                "cause": node,
                "impact": result.get("impact_score", 0),
                "cascade_size": len(result["affected_nodes"])
            })


def trigger_agent_pipeline(anomaly_event: dict):
    if not anomaly_event.get("anomaly"):
        return anomaly_event

    board = Boardroom(anomaly_event)

    node = anomaly_event.get("node_id", "Router-14")

    sim_res = simulate_impact(node, magnitude=150)
    board.add_simulation(node, sim_res)

    action_res = dispatch_tool("throttle", {
        "node_id": node,
        "params": {"pct": 50}
    })

    return {
        **anomaly_event,
        "simulation": sim_res,
        "action": action_res,
        "blackboard": board.blackboard
    }
