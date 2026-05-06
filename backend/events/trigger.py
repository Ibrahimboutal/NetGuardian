import logging
import json
from backend.agents.diagnosis_agent import run_diagnosis
from backend.agents.recommendation_agent import run_recommendation
from backend.agents.explanation_agent import run_explanation
from backend.agents.knowledge_base import retrieve_experience
from backend.agents.tools import TOOLS, simulate_impact

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
            "safety_checks": []
        }
        self.history = memory.get_context()

    def add_evidence(self, source: str, data: dict):
        self.blackboard["evidence"].append({"source": source, "data": data})

    def add_simulation(self, node: str, result: dict):
        self.blackboard["simulations"].append({"node": node, "result": result})

def trigger_agent_pipeline(anomaly_event: dict, progress_cb=None) -> dict:
    """
    Boardroom-Style Agentic Orchestration.
    Moves from linear pipeline to iterative reasoning.
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    def log_progress(msg: str):
        if progress_cb:
            progress_cb(msg)
        logger.info(f"💠 {msg}")

    # Initialize Shared Blackboard
    board = Boardroom(anomaly_event)
    log_progress("Initializing Boardroom Context...")
    
    # Step 1: Agentic Retrieval (Grounding)
    log_progress("Retrieving grounded infrastructure patterns...")
    experience = retrieve_experience(str(anomaly_event))
    board.add_evidence("KnowledgeBase", experience)

    # Step 2: First Pass - Reasoning & Tool Request
    log_progress("Gemma 4: Executing Initial Forensic Analysis...")
    diagnosis = run_diagnosis(anomaly_event, board.history, experience=experience)
    
    # Step 3: The Autonomous Loop (Real Agentic Depth)
    tool_results = None
    if diagnosis.get("tool_call"):
        tool_name = diagnosis["tool_call"].get("name")
        tool_args = diagnosis["tool_call"].get("args", {})
        
        if tool_name in TOOLS:
            log_progress(f"Agent Action: Requesting {tool_name} simulation...")
            tool_results = TOOLS[tool_name](**tool_args)
            board.add_simulation(tool_args.get("node_id"), tool_results)
            
            # REFINEMENT PASS: Re-evaluate diagnosis with new evidence
            log_progress("Refining hypothesis with simulation evidence...")
            diagnosis = run_diagnosis(
                anomaly_event, board.history, 
                experience=experience, 
                tool_output=tool_results,
                analysis_depth="SECOND_PASS_REFINEMENT"
            )

    # Step 4: Command & Safety (Boardroom Review)
    log_progress("Command Agent: Evaluating tactical interventions...")
    recommendation = run_recommendation(anomaly_event, diagnosis, board.get_context())
    board.blackboard["decisions"].append({
        "strategy": recommendation.get("decision"),
        "justification": recommendation.get("strategic_justification")
    })
    log_progress(f"Strategic Decision: {recommendation.get('decision')}")
    log_progress(f"Justification: {recommendation.get('strategic_justification')}")
    safety_status = "PASSED"
    if recommendation.get("actions"):
        log_progress("Safety Board: Verifying mitigation impact...")
        target = diagnosis.get("predicted_next_failure", "Unknown")
        sim = simulate_impact(target, "mitigation_validation")
        board.blackboard["safety_checks"].append(sim)
        if sim.get("affected_nodes_count", 0) > 8:
            safety_status = "RISK_DETECTED"
            log_progress("Safety Warning: Mitigation risk exceeds threshold!")

    # Step 5: Execution of Approved Mitigations
    action_results = []
    for action in recommendation.get("actions", []):
        if action.get("tool") and safety_status == "PASSED":
            log_progress(f"Executing: {action['action']} on target node...")
            res = TOOLS[action["tool"]](action["action"], diagnosis.get("predicted_next_failure"))
            action_results.append(res)

    # Step 6: Crisis Briefing
    log_progress("Generating final crisis briefing...")
    explanation = run_explanation(anomaly_event, diagnosis, recommendation, board.blackboard)

    result = {
        **anomaly_event,
        "belief_evolution": {
            "initial_confidence": diagnosis.get("confidence", 0.5),
            "safety_check": safety_status,
            "boardroom_cycles": 2 if tool_results else 1
        },
        "grounded_experience": experience,
        "simulation_results": tool_results,
        "mitigation_results": action_results,
        "agents": {
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
        "memory": memory.history,
    }
    
    memory.add(result)
    log_progress("Incident Stabilized. Briefing ready.")
    return result
