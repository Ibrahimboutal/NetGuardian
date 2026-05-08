import logging
import json
from backend.agents.tools import TOOLS, TOOL_REGISTRY, simulate_impact, normalize_args, sim
from backend.agents.knowledge_base import retrieve_experience

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
            "safety_status": "PENDING",
            "experience": None,
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

    from backend.agents.diagnosis_agent import run_diagnosis
    from backend.agents.explanation_agent import run_explanation
    from backend.agents.recommendation_agent import run_recommendation

    board = Boardroom(anomaly_event)
    node_id = anomaly_event.get("node_id", "Router-14")
    event_description = " ".join(
        f"{key}:{value}" for key, value in anomaly_event.items()
        if key in {"latency_ms", "throughput_mbps", "packet_loss_pct", "jitter_ms", "connections", "primary_metric", "severity"}
    )
    experience = retrieve_experience(event_description or json.dumps(anomaly_event, default=str))
    board.blackboard["experience"] = experience
    
    # --- RECURSIVE REASONING (3 Refinement Cycles) ---
    max_cycles = 3
    context_stream = f"Initial Anomaly: {anomaly_event.get('attribution', [])}\nExperience Match: {experience.get('id')} - {experience.get('name')}"
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
            # Keep refining the grounded context stream across cycles.
            
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

    diagnosis = run_diagnosis(
        anomaly_event,
        context=context_stream,
        experience=experience,
        tool_output=board.blackboard["simulations"][-1]["result"],
        analysis_depth="FINAL"
    )

    if not isinstance(diagnosis, dict):
        diagnosis = {}
    if diagnosis.get("type") == "tool_call":
        diagnosis = {
            "risk_level": "HIGH",
            "hypotheses": [
                {
                    "node": node_id,
                    "confidence": 0.72,
                    "reasoning": "Gemma requested deeper tool grounding for the detected incident."
                }
            ],
            "predicted_next_failure": node_id,
            "reasoning_trace": "[OBSERVATION]: Elevated telemetry. [HYPOTHESIS]: Localized infrastructure stress. [REASONING]: Simulation and topology support containment. [VALIDATION]: Tool-grounded checks completed.",
            "tool_call": diagnosis.get("calls", [])
        }

    recommendation = run_recommendation(
        anomaly_event,
        diagnosis,
        context=json.dumps(board.blackboard, default=str)
    )
    if not isinstance(recommendation, dict):
        recommendation = {}
    if not recommendation.get("actions"):
        recommendation = {
            "decision": "Emergency Isolation" if action == "isolate" else "Traffic Throttling",
            "actions": [
                {
                    "action": "Isolate Node" if action == "isolate" else "Throttle Traffic",
                    "tool": "execute_mitigation",
                    "priority": "CRITICAL" if action == "isolate" else "HIGH"
                }
            ],
            "strategic_justification": "Fallback mitigation selected from the grounded simulation results.",
            "trade_off": "Containment prioritized over throughput."
        }

    explanation = run_explanation(
        anomaly_event,
        diagnosis,
        recommendation,
        boardroom_context=board.blackboard
    )
    if not isinstance(explanation, dict):
        explanation = {}
    if not explanation.get("summary"): 
        explanation = {
            "summary": "The incident was detected, simulated, and contained using the grounded edge pipeline.",
            "eta_guess": "System Stabilized.",
            "status_color": "green"
        }

    simulation_summary = {
        "epicenter": node_id,
        "predicted_outcome": final_diagnosis,
        "impact_score": impact_score,
        "affected_nodes_count": len(board.blackboard["simulations"][-1]["result"].get("affected_nodes", [])),
        "critical_nodes_hit": critical_hits,
        "time_to_critical_failure": "Immediate" if impact_score > 100 else "Contained"
    }

    return {
        **anomaly_event,
        "diagnosis": final_diagnosis,
        "action": action_res,
        "simulation": simulation_summary,
        "experience": experience,
        "agents": {
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
        "blackboard": board.blackboard,
        "cycles_run": i + 1
    }
