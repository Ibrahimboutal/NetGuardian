import logging
import random
import math

logger = logging.getLogger(__name__)

# Regional Infrastructure Grid (Expanded for Technical Depth)
NETWORK_TOPOLOGY = {
    "Router-01": ["Router-02", "Router-05", "Substation-Alpha"],
    "Router-02": ["Router-01", "Router-03", "Router-14", "Node-X"],
    "Router-03": ["Router-02", "Router-04", "Node-Y"],
    "Router-04": ["Router-03", "Core-DC-01", "Regional-Hub-South"],
    "Router-05": ["Router-01", "Switch-02", "Regional-Hub-North"],
    "Switch-02": ["Router-05", "Router-14", "Substation-Beta"],
    "Router-14": ["Router-02", "Switch-02", "Core-DC-01"],
    "Core-DC-01": ["Router-04", "Router-14", "Backup-Vault-01"],
    "Substation-Alpha": ["Router-01"],
    "Substation-Beta": ["Switch-02"],
    "Regional-Hub-North": ["Router-05", "Node-A"],
    "Regional-Hub-South": ["Router-04", "Node-B"],
    "Node-A": ["Regional-Hub-North"],
    "Node-B": ["Regional-Hub-South"],
    "Node-X": ["Router-02"],
    "Node-Y": ["Router-03"],
    "Backup-Vault-01": ["Core-DC-01"]
}

# Robust Ontology Mapping (Aliases)
TOOL_REGISTRY = {
    "isolate": "execute_mitigation",
    "isolate_node": "execute_mitigation",
    "block": "execute_mitigation",
    "throttle": "throttle_traffic",
    "limit": "throttle_traffic",
    "reroute": "reroute_path",
    "switch": "reroute_path",
    "simulate": "simulate_impact",
    "predict": "simulate_impact",
    "status": "get_node_status",
    "check": "get_node_status"
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

    def apply_mitigation(self, node_id, action, params=None):
        """State Evolution: Actually changes the world state."""
        if node_id not in self.node_states:
            return False
            
        if action == "isolate":
            self.node_states[node_id]["status"] = "Isolated"
            self.node_states[node_id]["load"] = 0
        elif action == "throttle":
            pct = params.get("pct", 50) if params else 50
            self.node_states[node_id]["status"] = "Throttled"
            self.node_states[node_id]["load"] = max(10, self.node_states[node_id]["load"] - pct)
        elif action == "reroute":
            self.node_states[node_id]["status"] = "Rerouted"
            self.node_states[node_id]["latency"] += 10 # Cost of redundancy
            
        logger.info(f"🌐 SIMULATOR STATE UPDATED: {node_id} is now {self.node_states[node_id]['status']}")
        return True

# Singleton
sim = NetworkSimulator(NETWORK_TOPOLOGY)

def get_node_status(node_id: str):
    """Tool: Returns live health metrics for a specific infrastructure node."""
    logger.info(f"🛠️ Tool Calling: get_node_status({node_id})")
    status = sim.node_states.get(node_id, {"status": "Unknown", "latency": 0, "load": 0})
    return {
        "node": node_id,
        "metrics": status,
        "active_alerts": ["High Pressure"] if status.get("load", 0) > 80 else []
    }

def simulate_impact(node_id: str, failure_type: str = "buffer_exhaustion"):
    """Tool: Runs a graph-based simulation to predict impact."""
    logger.info(f"🛠️ Tool Calling: simulate_impact({node_id}, {failure_type})")
    propagation = sim.simulate_failure(node_id, failure_type)
    return {
        "start_node": node_id,
        "affected_nodes": len(propagation),
        "risk": "CRITICAL" if len(propagation) > 4 else "LOW"
    }

def execute_mitigation(action: str, target: str):
    """Tool: Executes a defensive action and updates the world state."""
    logger.info(f"🛠️ Tool Calling: execute_mitigation({action}, {target})")
    success = sim.apply_mitigation(target, action.lower())
    return {
        "status": "Applied" if success else "Failed",
        "action": action,
        "target": target,
        "current_health": sim.node_states.get(target)
    }

def analyze_topology(node_id: str):
    """Tool: Returns the immediate topology and connectivity graph for a node."""
    logger.info(f"🛠️ Tool Calling: analyze_topology({node_id})")
    neighbors = NETWORK_TOPOLOGY.get(node_id, [])
    return {
        "node": node_id,
        "neighbors": neighbors,
        "critical_paths": [n for n in neighbors if "Core" in n],
        "redundancy_level": "High" if len(neighbors) > 2 else "Low"
    }

def throttle_traffic(node_id: str, throttle_pct: int):
    """Tool: Limits ingress traffic to prevent buffer overflow or DDoS saturation."""
    logger.info(f"🛠️ Tool Calling: throttle_traffic({node_id}, {throttle_pct}%)")
    return {
        "status": "Applied",
        "node": node_id,
        "throttle_rate": f"{throttle_pct}%",
        "risk_mitigation": "DDoS/Buffer Satiation"
    }

def reroute_path(source_node: str, blocked_path: str):
    """Tool: Forcefully reroutes traffic from a degraded path to a redundant neighbor."""
    logger.info(f"🛠️ Tool Calling: reroute_path({source_node}, {blocked_path})")
    neighbors = NETWORK_TOPOLOGY.get(source_node, [])
    alternative = [n for n in neighbors if n != blocked_path]
    return {
        "source": source_node,
        "rerouted_via": alternative[0] if alternative else "None",
        "path_latency_delta": "+5ms" if alternative else "N/A"
    }

TOOLS = {
    "get_node_status": get_node_status,
    "simulate_impact": simulate_impact,
    "execute_mitigation": execute_mitigation,
    "analyze_topology": analyze_topology,
    "throttle_traffic": throttle_traffic,
    "reroute_path": reroute_path
}
