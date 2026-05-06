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
    Allows agents to share state, hypotheses, and tool results.
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
            "safety_checks": []
        }
        self.history = memory.get_context()

    def add_evidence(self, source: str, data: dict):
        self.blackboard["evidence"].append({"source": source, "data": data})

    def add_simulation(self, node: str, result: dict):
        self.blackboard["simulations"].append({"node": node, "result": result})
        
    def check_for_conflicts(self, diagnosis: dict):
        """High-Impact: Detects if Gemma 4 is providing contradictory theories."""
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

def dispatch_tool(tool_call_request: dict) -> dict:
    """Robust & Ontology-Aware Tool Dispatcher."""
    from backend.agents.tools import TOOL_REGISTRY
    try:
        raw_func_name = tool_call_request["function"]["name"]
        # Ontology Mapping: Convert LLM aliases to canonical Python names
        func_name = TOOL_REGISTRY.get(raw_func_name.lower(), raw_func_name)
        
        args = json.loads(tool_call_request["function"]["arguments"])
        
        if func_name in TOOLS:
            logger.info(f"⚡ Dispatching Canonical Tool: {func_name}")
            return TOOLS[func_name](**args)
        return {"error": f"Tool '{func_name}' not found in registry."}
    except Exception as e:
        logger.error(f"Tool Dispatch Error: {e}")
        return {"error": str(e)}

def trigger_agent_pipeline(anomaly_event: dict, progress_cb=None) -> dict:
    """
    Advanced Recursive Boardroom Orchestration.
    Allows for multi-step tool chaining and stateful refinement.
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    def log_progress(msg: str):
        if progress_cb:
            progress_cb(msg)
        logger.info(f"💠 {msg}")

    # Initialize Boardroom
    board = Boardroom(anomaly_event)
    log_progress("Initializing Boardroom Context...")
    
    # Grounding
    experience = retrieve_experience(str(anomaly_event))
    board.add_evidence("KnowledgeBase", experience)

    # --- THE RECURSIVE LOOP (Multi-Tool Chaining) ---
    max_iterations = 3
    current_diagnosis = None
    i = 0
    
    for i in range(max_iterations):
        log_progress(f"Boardroom Cycle {i+1}: Analyzing evidence...")
        
        # Diagnosis Agent can request tools
        current_diagnosis = run_diagnosis(
            anomaly_event, 
            board.get_context(), 
            experience=experience,
            analysis_depth="DEEP_RECURSION" if i > 0 else "INITIAL"
        )
        
        # If it's a tool call, dispatch it and continue the loop
        if isinstance(current_diagnosis, dict) and current_diagnosis.get("type") == "tool_call":
            call = current_diagnosis["calls"][0]
            tool_name = call["function"]["name"]
            
            log_progress(f"Agent Logic: Chaining tool '{tool_name}'...")
            res = dispatch_tool(call)
            board.add_simulation(tool_name, res)
            
            # CONFLICT CHECK: Does this new evidence contradict our previous hypothesis?
            if board.check_for_conflicts(current_diagnosis):
                log_progress("RESOLUTION TRIGGERED: Contradictory evidence detected. Re-evaluating...")
                
            log_progress(f"Tool Evidence Integrated: {tool_name} success.")
            continue 
        else:
            log_progress("Hypothesis Stabilized. Moving to Tactical Command.")
            break

    # Step 4: Command & Safety (Stateful)
    log_progress("Command Agent: Formulating intervention strategy...")
    recommendation = run_recommendation(anomaly_event, current_diagnosis, board.get_context())
    
    board.blackboard["decisions"].append({
        "strategy": recommendation.get("decision"),
        "justification": recommendation.get("strategic_justification")
    })
    
    # Safety Validation
    safety_status = "PASSED"
    if recommendation.get("actions"):
        log_progress("Safety Board: Simulating mitigation side-effects...")
        target = current_diagnosis.get("predicted_next_failure", "Unknown")
        sim_res = simulate_impact(target, "mitigation_validation")
        board.blackboard["safety_checks"].append(sim_res)
        
        if sim_res.get("affected_nodes", 0) > 6:
            safety_status = "RISK_WARNING"
            log_progress("Safety Warning: High potential for collateral service loss.")

    # Step 5: Execution (World-State Change)
    action_results = []
    for action in recommendation.get("actions", []):
        if action.get("tool") and safety_status != "BLOCKED":
            log_progress(f"Executing Mitigation: {action['action']}...")
            # Robust tool execution
            res = execute_mitigation(action.get("tool_action", action["action"]), current_diagnosis.get("predicted_next_failure"))
            action_results.append(res)

    # Final Briefing
    log_progress("Finalizing Crisis Briefing...")
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
