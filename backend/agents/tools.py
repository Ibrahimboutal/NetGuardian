import logging
import random

logger = logging.getLogger(__name__)

# Basic Network Topology Graph
# Nodes: Routers, Edges: Connections
NETWORK_TOPOLOGY = {
    "Router-01": ["Router-02", "Router-05"],
    "Router-02": ["Router-01", "Router-03", "Router-14"],
    "Router-03": ["Router-02", "Router-04"],
    "Router-04": ["Router-03", "Core-DC-01"],
    "Router-05": ["Router-01", "Switch-02"],
    "Switch-02": ["Router-05", "Router-14"],
    "Router-14": ["Router-02", "Switch-02", "Core-DC-01"],
    "Core-DC-01": ["Router-04", "Router-14"]
}

class NetworkSimulator:
    """
    Simulates Failure Propagation across a network graph.
    """
    def __init__(self, topology):
        self.topology = topology
        self.node_states = {node: {"latency": 20, "load": 10, "status": "Healthy"} for node in topology}

    def simulate_failure(self, start_node, failure_type):
        """
        Propagates a failure from a start node to its neighbors.
        """
        affected = {}
        queue = [(start_node, 1.0)] # node, impact_factor
        visited = set()
        
        while queue:
            node, factor = queue.pop(0)
            if node in visited or factor < 0.2:
                continue
            visited.add(node)
            
            # Apply impact
            impact = {
                "latency_increase": int(200 * factor),
                "load_increase": int(50 * factor),
                "status": "Critical" if factor > 0.8 else "Degraded"
            }
            affected[node] = impact
            
            # Propagate to neighbors with reduced factor
            for neighbor in self.topology.get(node, []):
                queue.append((neighbor, factor * 0.6))
        
        return affected

# Singleton
sim = NetworkSimulator(NETWORK_TOPOLOGY)

def get_node_status(node_id: str):
    """Tool: Returns live health metrics for a specific infrastructure node."""
    logger.info(f"🛠️ Tool Calling: get_node_status({node_id})")
    status = sim.node_states.get(node_id, {"status": "Unknown"})
    return {
        "node": node_id,
        "metrics": status,
        "active_alerts": ["Thermal Warning"] if status.get("load", 0) > 80 else []
    }

def simulate_impact(node_id: str, failure_type: str):
    """Tool: Runs a graph-based simulation to predict the impact of a node failure."""
    logger.info(f"🛠️ Tool Calling: simulate_impact({node_id}, {failure_type})")
    propagation = sim.simulate_failure(node_id, failure_type)
    
    return {
        "start_node": node_id,
        "failure_type": failure_type,
        "affected_nodes_count": len(propagation),
        "propagation_map": propagation,
        "predicted_outcome": "Cascading Failure" if len(propagation) > 3 else "Isolated Incident",
        "time_to_critical_failure": "45-90 seconds"
    }

def execute_mitigation(action: str, target: str):
    """Tool: Executes a defensive action (ACL update, traffic rerouting, node isolation)."""
    logger.info(f"🛠️ Tool Calling: execute_mitigation({action}, {target})")
    return {
        "status": "Success",
        "intervention": action,
        "target": target,
        "impact_recovery_est": "15 minutes"
    }

TOOLS = {
    "get_node_status": get_node_status,
    "simulate_impact": simulate_impact,
    "execute_mitigation": execute_mitigation
}
