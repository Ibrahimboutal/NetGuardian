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

# Infrastructure Criticality (The "Importance" Factor)
NODE_CRITICALITY = {
    "Core-DC-01": 10,
    "Backup-Vault-01": 9,
    "Regional-Hub-North": 7,
    "Regional-Hub-South": 7,
    "Router-01": 5, "Router-02": 5, "Router-14": 8,
    "Node-A": 2, "Node-B": 2, "Substation-Alpha": 4, "Substation-Beta": 4
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
    def __init__(self, topology):
        self.topology = topology
        self.node_states = {node: {"latency": 20, "load": 10, "status": "Healthy"} for node in topology}

    def simulate_failure(self, start_node, failure_type="cascade"):
        """
        Advanced Stateful Propagation: Respects active mitigations and criticality.
        If a node is Isolated, spread stops. If Throttled, spread is slowed.
        """
        affected = {start_node}
        queue = [(start_node, 1.0)] # node, probability of spread
        total_impact_score = 0
        
        while queue:
            current, prob = queue.pop(0)
            state = self.node_states.get(current, {})
            status = state.get("status", "Healthy")
            
            # --- MITIGATION FEEDBACK LOOP ---
            if status == "Isolated": 
                continue # The wall: Spread stops at isolated nodes
            
            effective_prob = prob
            if status == "Throttled":
                effective_prob *= 0.2 # 80% reduction in propagation risk
            
            # Weighted impact calculation
            total_impact_score += NODE_CRITICALITY.get(current, 1) * effective_prob
            
            if effective_prob < 0.2: continue # Failure fizzled out
            
            for neighbor in self.topology.get(current, []):
                if neighbor not in affected:
                    affected.add(neighbor)
                    queue.append((neighbor, effective_prob * 0.7)) # Spatial decay
        
        return {
            "affected_nodes_count": len(affected),
            "impact_score": round(total_impact_score, 2),
            "critical_nodes_hit": [n for n in affected if NODE_CRITICALITY.get(n, 0) >= 8],
            "containment_status": "Successful" if len(affected) < 3 else "Partial"
        }

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
    return propagation

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
        "critical_paths": [n for n in neighbors if NODE_CRITICALITY.get(n, 0) >= 8],
        "redundancy_level": "High" if len(neighbors) > 2 else "Low"
    }

def throttle_traffic(node_id: str, throttle_pct: int):
    """Tool: Limits ingress traffic to prevent buffer overflow or DDoS saturation."""
    logger.info(f"🛠️ Tool Calling: throttle_traffic({node_id}, {throttle_pct}%)")
    success = sim.apply_mitigation(node_id, "throttle", {"pct": throttle_pct})
    return {
        "status": "Applied" if success else "Failed",
        "node": node_id,
        "throttle_rate": f"{throttle_pct}%",
        "risk_mitigation": "DDoS/Buffer Satiation"
    }

def reroute_path(source_node: str, blocked_path: str):
    """Tool: Forcefully reroutes traffic from a degraded path to a redundant neighbor."""
    logger.info(f"🛠️ Tool Calling: reroute_path({source_node}, {blocked_path})")
    success = sim.apply_mitigation(source_node, "reroute")
    neighbors = NETWORK_TOPOLOGY.get(source_node, [])
    alternative = [n for n in neighbors if n != blocked_path]
    return {
        "source": source_node,
        "rerouted_via": alternative[0] if alternative else "None",
        "status": "Success" if success else "Failed"
    }

TOOLS = {
    "get_node_status": get_node_status,
    "simulate_impact": simulate_impact,
    "execute_mitigation": execute_mitigation,
    "analyze_topology": analyze_topology,
    "throttle_traffic": throttle_traffic,
    "reroute_path": reroute_path
}
