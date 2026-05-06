import logging
import random
import math

logger = logging.getLogger(__name__)

# Regional Infrastructure Grid
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

NODE_METRICS = {
    "Core-DC-01": {"criticality": 10, "capacity": 1000},
    "Backup-Vault-01": {"criticality": 9, "capacity": 500},
    "Router-14": {"criticality": 8, "capacity": 400},
    "Router-01": {"criticality": 5, "capacity": 300},
    "Router-02": {"criticality": 5, "capacity": 300},
    "Substation-Alpha": {"criticality": 4, "capacity": 200},
    "Substation-Beta": {"criticality": 4, "capacity": 200},
}

class NetworkSimulator:
    def __init__(self, topology):
        self.topology = topology
        self.node_states = {
            node: {
                "status": "Healthy", 
                "load": 20, 
                "capacity": NODE_METRICS.get(node, {}).get("capacity", 150),
                "criticality": NODE_METRICS.get(node, {}).get("criticality", 2)
            } for node in topology
        }

    def find_path(self, start, end, avoid=None):
        queue = [[start]]
        visited = {start}
        if avoid: visited.add(avoid)
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == end: return path
            for neighbor in self.topology.get(node, []):
                if neighbor not in visited and self.node_states[neighbor]["status"] != "Isolated":
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def simulate_failure(self, epicenter, magnitude=100):
        if epicenter not in self.node_states:
            epicenter = "Router-14"
            
        affected = {epicenter}
        queue = [(epicenter, magnitude)]
        total_impact = 0
        
        while queue:
            current, spillover = queue.pop(0)
            state = self.node_states[current]
            if state["status"] == "Isolated": continue
            
            damage = spillover * (state["criticality"] / 5.0)
            total_impact += damage
            
            if spillover > state["capacity"] * 0.5:
                for neighbor in self.topology.get(current, []):
                    if neighbor not in affected:
                        affected.add(neighbor)
                        queue.append((neighbor, spillover * 0.6))
                        
        return {
            "epicenter": epicenter,
            "impact_score": round(total_impact, 2),
            "affected_nodes": list(affected),
            "critical_nodes_hit": [n for n in affected if self.node_states[n]["criticality"] >= 8]
        }

    def apply_mitigation(self, node_id, action, params=None):
        if node_id not in self.node_states: return False
        state = self.node_states[node_id]
        if action == "isolate":
            state["status"] = "Isolated"
            state["load"] = 0
        elif action == "throttle":
            pct = params.get("pct", 50) if params else 50
            state["status"] = "Throttled"
            state["load"] *= (1 - pct/100.0)
        elif action == "reroute":
            state["status"] = "Rerouted"
        return True

sim = NetworkSimulator(NETWORK_TOPOLOGY)

# --- UNIFIED TOOL PROTOCOL (The Schema Layer) ---

TOOL_SCHEMA = {
    "execute_mitigation": ["node_id", "action", "params"],
    "simulate_impact": ["node_id", "magnitude"],
    "reroute_path": ["node_id", "target", "blocked_node"],
    "get_node_status": ["node_id"],
    "analyze_topology": ["node_id"]
}

def normalize_args(tool_name, args):
    """Normalization layer to catch LLM variations."""
    if tool_name == "execute_mitigation":
        return {
            "node_id": args.get("node_id") or args.get("target"),
            "action": args.get("action", "throttle"),
            "params": args.get("params", {"pct": args.get("throttle_pct", 50)})
        }
    elif tool_name == "simulate_impact":
        return {
            "node_id": args.get("node_id") or args.get("node"),
            "magnitude": args.get("magnitude", 150)
        }
    elif tool_name == "reroute_path":
        return {
            "node_id": args.get("node_id") or args.get("source"),
            "target": args.get("target", "Core-DC-01"),
            "blocked_node": args.get("blocked_node") or args.get("blocked_path")
        }
    return args

def get_node_status(node_id: str):
    return {"node": node_id, "data": sim.node_states.get(node_id)}

def simulate_impact(node_id: str, magnitude: int = 200):
    return sim.simulate_failure(node_id, magnitude)

def execute_mitigation(node_id: str, action: str, params: dict = None):
    success = sim.apply_mitigation(node_id, action, params)
    return {"status": "Success" if success else "Failed", "node": node_id, "action": action}

def reroute_path(node_id: str, target: str, blocked_node: str):
    path = sim.find_path(node_id, target, avoid=blocked_node)
    if path:
        sim.apply_mitigation(node_id, "reroute")
        return {"status": "Success", "new_path": path}
    return {"status": "Failed", "error": "No alternative path found"}

def analyze_topology(node_id: str):
    return {
        "node": node_id,
        "neighbors": NETWORK_TOPOLOGY.get(node_id, []),
        "criticality": NODE_METRICS.get(node_id, {}).get("criticality", 1)
    }

TOOLS = {
    "get_node_status": get_node_status,
    "simulate_impact": simulate_impact,
    "execute_mitigation": execute_mitigation,
    "reroute_path": reroute_path,
    "analyze_topology": analyze_topology
}

TOOL_REGISTRY = {
    "isolate": "execute_mitigation", "throttle": "execute_mitigation",
    "reroute": "reroute_path", "check": "get_node_status",
    "predict": "simulate_impact"
}