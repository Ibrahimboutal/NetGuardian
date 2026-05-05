import logging
import json
import re
from backend.agents.diagnosis_agent import run_diagnosis
from backend.agents.recommendation_agent import run_recommendation
from backend.agents.explanation_agent import run_explanation
from backend.agents.knowledge_base import retrieve_experience
from backend.agents.tools import TOOLS

logger = logging.getLogger(__name__)

class AnomalyMemory:
    """Enterprise-grade store for incident history and pattern detection."""
    def __init__(self, limit=5):
        self.history = []
        self.limit = limit

    def add(self, event: dict):
        summary = {
            "timestamp": event.get("timestamp"),
            "issue": event.get("agents", {}).get("diagnosis", {}).get("risk_level", "Unknown"),
            "severity": event.get("severity")
        }
        self.history.insert(0, summary)
        self.history = self.history[:self.limit]

    def detect_pattern(self) -> str:
        if len(self.history) < 2:
            return "Stable / Baseline establishing."
        recent = self.history[:3]
        issues = [h['issue'].lower() for h in recent]
        if any("spike" in i for i in issues) and any("loss" in i or "drop" in i for i in issues):
            return "ALERT: Cascading Failure Pattern Detected (Escalation from Spikes to Packet Drops)."
        if len(set(issues)) == 1 and len(issues) >= 3:
            return "WARNING: Persistent / Sustained Incident Pattern."
        return "Active / Independent events."

    def get_context(self) -> str:
        if not self.history:
            return "[]"
        return json.dumps(self.history, indent=2)

# Initialize memory
memory = AnomalyMemory()

def execute_agent_tool(tool_call_str: str):
    if not tool_call_str:
        return None
    try:
        match = re.match(r"(\w+)\((.*)\)", tool_call_str)
        if not match:
            return None
        func_name = match.group(1)
        args_str = match.group(2)
        kwargs = {}
        for arg in args_str.split(','):
            if '=' in arg:
                k, v = arg.split('=')
                kwargs[k.strip()] = v.strip().strip("'").strip('"')
        if func_name in TOOLS:
            return TOOLS[func_name](**kwargs)
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
    return None

def trigger_agent_pipeline(anomaly_event: dict) -> dict:
    """
    Adaptive Agentic Pipeline v5:
    1. Grounding -> Initial Diagnosis (T1)
    2. Tool Execution -> Belief Evolution (T2)
    3. [Adaptive] Second Analysis Pass (if needed)
    4. Tactical Intervention (Trade-offs)
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    # Step 1: Explainable Retrieval
    experience = retrieve_experience(str(anomaly_event))
    pattern = memory.detect_pattern()
    context = memory.get_context()

    # Step 2: Initial Diagnosis (T1)
    initial_diagnosis = run_diagnosis(anomaly_event, context, pattern, experience)
    initial_confidence = initial_diagnosis.get("confidence", 0.5)

    # Step 3: Tool Execution & Adaptive Pass
    tool_output = None
    refined_diagnosis = initial_diagnosis
    confidence_delta = 0.0
    adaptive_pass = False

    if initial_diagnosis.get("tool_call"):
        tool_output = execute_agent_tool(initial_diagnosis["tool_call"])
        if tool_output:
            refined_diagnosis = run_diagnosis(anomaly_event, context, pattern, experience, tool_output=tool_output)
            
            # Adaptive second pass if AI is still uncertain
            if refined_diagnosis.get("needs_more_analysis"):
                logger.info("🔄 Agent 1: Initiating Adaptive Second Pass...")
                adaptive_pass = True
                refined_diagnosis = run_diagnosis(anomaly_event, context, pattern, experience, tool_output=tool_output)

            confidence_delta = round(refined_diagnosis.get("confidence", 0.5) - initial_confidence, 2)

    # Step 4: Final Tactical Planning
    recommendation = run_recommendation(anomaly_event, refined_diagnosis, context, pattern)
    
    # Execute mitigation
    action_results = []
    for action in recommendation.get("actions", []):
        if action.get("tool"):
            res = execute_agent_tool(f"{action['tool']}(action='{action['action']}', target='{refined_diagnosis['predicted_next_failure']}')")
            if res:
                action_results.append(res)

    # Step 5: Briefing
    explanation = run_explanation(anomaly_event, refined_diagnosis, recommendation, context, pattern)

    result = {
        **anomaly_event,
        "belief_evolution": {
            "initial_confidence": initial_confidence,
            "refined_confidence": refined_diagnosis.get("confidence", 0.5),
            "confidence_delta": confidence_delta,
            "adaptive_pass_triggered": adaptive_pass,
            "tool_used": initial_diagnosis.get("tool_call")
        },
        "grounded_experience": experience,
        "simulation_results": tool_output,
        "mitigation_results": action_results,
        "agents": {
            "diagnosis": refined_diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
        "memory": memory.history,
    }
    
    memory.add(result)
    return result
