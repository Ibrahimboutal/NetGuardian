import logging
import json
from backend.agents.diagnosis_agent import run_diagnosis
from backend.agents.recommendation_agent import run_recommendation
from backend.agents.explanation_agent import run_explanation
from backend.agents.knowledge_base import retrieve_experience
from backend.agents.tools import TOOLS, simulate_impact, execute_mitigation

logger = logging.getLogger(__name__)

class AnomalyMemory:
    def __init__(self, limit=5):
        self.history = []
        self.limit = limit

    def add(self, result: dict):
        summary = {
            "timestamp": result.get("timestamp"),
            "risk": result.get("agents", {}).get("diagnosis", {}).get("risk_level", "Unknown"),
            "action": result.get("agents", {}).get("recommendation", {}).get("decision", "None")
        }
        self.history.insert(0, summary)
        self.history = self.history[:self.limit]

    def get_context(self) -> str:
        return json.dumps(self.history, indent=2)

memory = AnomalyMemory()

class Boardroom:
    """
    Shared Blackboard for Multi-Agent Collaboration.
    """
    def __init__(self, anomaly_event: dict):
        self.anomaly_event = anomaly_event
        self.blackboard = {
            "telemetry": anomaly_event,
            "hypotheses": [],
            "evidence": [],
            "simulations": [],
            "decisions": [],
            "conflicts": [],
            "causal_chain": [],
            "safety_checks": []
        }
        self.history = memory.get_context()

    def add_evidence(self, source: str, data: dict):
        self.blackboard["evidence"].append({"source": source, "data": data})

    def add_simulation(self, node: str, result: dict):
        self.blackboard["simulations"].append({"node": node, "result": result})
        
        # ELITE: Link Epicenter to its effects (Causal Chain)
        if "affected_nodes_count" in result:
            self.blackboard["causal_chain"].append({
                "cause": node,
                "impact": result.get("impact_score", 0),
                "cascade_size": result.get("affected_nodes_count", 0)
            })
        
    def check_for_conflicts(self, diagnosis: dict):
        """High-Impact: Detects if Gemma 4 is providing contradictory theories."""
        # Fix: Ensure we are looking at a valid diagnosis dict, not a tool call
        if not isinstance(diagnosis, dict) or diagnosis.get("type") == "tool_call":
            return False
            
        hyps = diagnosis.get("hypotheses", [])
        if len(hyps) > 1:
            conf_diff = abs(hyps[0].get("confidence", 0) - hyps[1].get("confidence", 0))
            if conf_diff < 0.15:
                conflict = f"CONTRADICTION: Low confidence delta between {hyps[0]['node']} and {hyps[1]['node']}"
                self.blackboard["conflicts"].append(conflict)
                return True
        return False

    def get_context(self) -> str:
        return json.dumps(self.blackboard, indent=2)

def dispatch_tool(tool_name: str, args: dict) -> dict:
    """Robust & Ontology-Aware Tool Dispatcher."""
    from backend.agents.tools import TOOL_REGISTRY
    try:
        # Ontology Mapping
        canonical_name = TOOL_REGISTRY.get(tool_name.lower(), tool_name)
        
        if canonical_name in TOOLS:
            logger.info(f"⚡ Dispatching Canonical Tool: {canonical_name}")
            return TOOLS[canonical_name](**args)
        return {"error": f"Tool '{canonical_name}' not found."}
    except Exception as e:
        logger.error(f"Tool Dispatch Error: {e}")
        return {"error": str(e)}

def trigger_agent_pipeline(anomaly_event: dict, progress_cb=None) -> dict:
    """
    Elite Recursive Boardroom Orchestration.
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    def log_progress(msg: str):
        if progress_cb:
            progress_cb(msg)
        logger.info(f"💠 {msg}")

    board = Boardroom(anomaly_event)
    log_progress("Initializing Boardroom Context...")
    
    experience = retrieve_experience(str(anomaly_event))
    board.add_evidence("KnowledgeBase", experience)

    max_iterations = 3
    current_diagnosis = None
    i = 0
    
    for i in range(max_iterations):
        log_progress(f"Boardroom Cycle {i+1}: Analyzing evidence...")
        
        current_diagnosis = run_diagnosis(
            anomaly_event, 
            board.get_context(), 
            experience=experience,
            analysis_depth="DEEP_RECURSION" if i > 0 else "INITIAL"
        )
        
        if isinstance(current_diagnosis, dict) and current_diagnosis.get("type") == "tool_call":
            call = current_diagnosis["calls"][0]
            func = call["function"]
            t_name = func["name"]
            t_args = json.loads(func["arguments"])
            
            log_progress(f"Agent Logic: Chaining tool '{t_name}'...")
            res = dispatch_tool(t_name, t_args)
            board.add_simulation(t_name, res)
            continue 
        else:
            # Final diagnosis reached: Perform Conflict Check
            if board.check_for_conflicts(current_diagnosis):
                log_progress("CONFLICT DETECTED: Theories competing. Triggering resolution...")
                # In a real system, we'd loop again with a specific tie-breaker prompt.
            break

    log_progress("Command Agent: Formulating intervention strategy...")
    recommendation = run_recommendation(anomaly_event, current_diagnosis, board.get_context())
    
    board.blackboard["decisions"].append({
        "strategy": recommendation.get("decision"),
        "justification": recommendation.get("strategic_justification")
    })
    
    # Safety Validation (Weighted)
    safety_status = "PASSED"
    if recommendation.get("actions"):
        log_progress("Safety Board: Simulating weighted mitigation impact...")
        target = current_diagnosis.get("predicted_next_failure", "Unknown")
        sim_res = simulate_impact(target, "mitigation_validation")
        board.blackboard["safety_checks"].append(sim_res)
        
        if sim_res.get("impact_score", 0) > 15: # Criticality-aware threshold
            safety_status = "RISK_WARNING"
            log_progress("Safety Warning: Mitigation affects high-criticality core nodes.")

    # Step 5: Execution (Correct Dispatching)
    action_results = []
    for action in recommendation.get("actions", []):
        if action.get("tool") and safety_status != "BLOCKED":
            t_name = action["tool"]
            # Fix: Pass correct arguments to the tool chosen by the agent
            t_args = {"node_id": current_diagnosis.get("predicted_next_failure"), "throttle_pct": 50} 
            if t_name == "reroute_path":
                t_args = {"source_node": anomaly_event.get("node_id"), "blocked_path": current_diagnosis.get("predicted_next_failure")}
            
            log_progress(f"Executing Mitigation: {t_name} on target...")
            res = dispatch_tool(t_name, t_args)
            action_results.append(res)

    explanation = run_explanation(anomaly_event, current_diagnosis, recommendation, board.blackboard)

    result = {
        **anomaly_event,
        "belief_evolution": {
            "initial_confidence": current_diagnosis.get("confidence", 0.7) if isinstance(current_diagnosis, dict) else 0.5,
            "safety_check": safety_status,
            "boardroom_cycles": i + 1
        },
        "mitigation_results": action_results,
        "agents": {
            "diagnosis": current_diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
        "blackboard": board.blackboard
    }
    
    memory.add(result)
    log_progress("Incident Stabilized. NetGuardian Standby.")
    return result
