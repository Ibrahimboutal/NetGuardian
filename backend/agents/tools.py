import logging
import random
import math

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
    Simulates Failure Propagation across a network graph using Distance-Based Decay.
    """
    def __init__(self, topology):
        self.topology = topology
        self.node_states = {node: {"latency": 20, "load": 10, "status": "Healthy"} for node in topology}

    def simulate_failure(self, start_node, failure_type):
        """
        Propagates a failure using an Inverse Distance Weighting (IDW) model.
        The impact decays as a function of 'hops' from the epicenter.
        """
        affected = {}
        # Queue stores: (node, current_distance/hops)
        queue = [(start_node, 0)] 
        visited = {start_node: 0}
        
        while queue:
            node, hops = queue.pop(0)
            
            # Impact factor decays using inverse distance: 1 / (hops + 1)
            # This makes the propagation modeling feel much more algorithmic.
            factor = 1.0 / (hops + 1.0)
            
            if factor < 0.2: # Prune very distant nodes
                continue
                
            # Apply impact with logarithmic scaling for load
            impact = {
                "hops_from_source": hops,
                "latency_increase": int(250 * factor),
                "load_increase": int(100 * math.log(hops + 2, 2) * factor), # Logarithmic pressure
                "status": "Critical" if factor > 0.7 else ("Degraded" if factor > 0.4 else "At Risk")
            }
            affected[node] = impact
            
            # Propagate to neighbors
            for neighbor in self.topology.get(node, []):
                if neighbor not in visited or visited[neighbor] > hops + 1:
                    visited[neighbor] = hops + 1
                    queue.append((neighbor, hops + 1))
        
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
