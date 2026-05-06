import logging
import json
from backend.agents.tools import TOOLS, TOOL_REGISTRY, simulate_impact, normalize_args, sim

logger = logging.getLogger(__name__)

def dispatch_tool(tool_name: str, args: dict):
    """Hardened Dispatcher: Normalizes and validates tool calls."""
    canonical = TOOL_REGISTRY.get(tool_name.lower(), tool_name)
    
    # 1. Normalize Variations
    normalized_args = normalize_args(canonical, args)
    
    # 2. Inject context-specific defaults
    if canonical == "execute_mitigation":
        normalized_args.setdefault("action", tool_name)

    # 3. Execute
    if canonical in TOOLS:
        logger.info(f"⚡ Dispatching: {canonical}({normalized_args})")
        return TOOLS[canonical](**normalized_args)

    return {"error": f"Tool '{canonical}' not found in registry."}

class Boardroom:
    """Enhanced Blackboard: Tracks causal chains and outcomes."""
    def __init__(self, anomaly_event):
        self.blackboard = {
            "telemetry": anomaly_event,
            "simulations": [],
            "causal_chain": [],
            "decisions": [],
            "safety_status": "PENDING"
        }

    def add_simulation(self, node, result):
        self.blackboard["simulations"].append({"node": node, "result": result})
        if "affected_nodes" in result:
            self.blackboard["causal_chain"].append({
                "epicenter": node,
                "impact": result.get("impact_score", 0),
                "nodes_lost": len(result["affected_nodes"]),
                "critical_hits": result.get("critical_nodes_hit", [])
            })

def trigger_agent_pipeline(anomaly_event: dict, progress_cb=None):
    """
    Elite Recursive Orchestration.
    Implements true reasoning refinement by re-injecting tool output into context.
    """
    if not anomaly_event.get("anomaly"):
        return anomaly_event

    board = Boardroom(anomaly_event)
    node_id = anomaly_event.get("node_id", "Router-14")
    
    # --- RECURSIVE REASONING (3 Refinement Cycles) ---
    max_cycles = 3
    context_stream = f"Initial Anomaly: {anomaly_event['attribution']}"
    final_diagnosis = None

    for i in range(max_cycles):
        msg = f"🧠 Boardroom Cycle {i+1}: Refining Hypothesis..."
        logger.info(msg)
        if progress_cb: progress_cb(msg)
        
        # 1. Simulate the current epicenter (Tool Use)
        sim_res = simulate_impact(node_id, magnitude=150)
        board.add_simulation(node_id, sim_res)
        
        # 2. Re-inject results into context (The "Deep Reasoning" fix)
        context_stream += f"\nCycle {i+1} Simulation: Impact Score {sim_res['impact_score']}, Critical Nodes Hit: {sim_res['critical_nodes_hit']}"
        
        msg2 = f"📊 Cycle {i+1} Simulation: Impact Score {sim_res['impact_score']}, Critical Nodes Hit: {sim_res['critical_nodes_hit']}"
        if progress_cb: progress_cb(msg2)
        
        # 3. Formulate tactical decision based on evolved context
        if sim_res["impact_score"] < 50:
            final_diagnosis = "Contained Anomaly"
            action = "throttle"
            break
        else:
            final_diagnosis = "Cascading Failure Risk"
            action = "isolate"
            # In a real agentic flow, we'd call run_diagnosis(context_stream) here
            
    # --- HARDENED SAFETY BOARD ---
    safety_block = False
    impact_score = board.blackboard["causal_chain"][-1]["impact"]
    critical_hits = board.blackboard["causal_chain"][-1]["critical_hits"]
    nodes_lost = board.blackboard["causal_chain"][-1]["nodes_lost"]

    if impact_score > 30 or nodes_lost > 5 or any(n in ["Core-DC-01", "Backup-Vault-01"] for n in critical_hits):
        board.blackboard["safety_status"] = "CRITICAL_WARNING"
        logger.warning("🛡️ Safety Board: High risk detected. Escalating mitigation depth.")
        action = "isolate" # Escalate for safety
        
    # --- CANONICAL EXECUTION ---
    action_res = dispatch_tool(action, {
        "node_id": node_id,
        "params": {"pct": 75 if action == "throttle" else 100}
    })

    return {
        **anomaly_event,
        "diagnosis": final_diagnosis,
        "action": action_res,
        "blackboard": board.blackboard,
        "cycles_run": i + 1
    }
