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
    """
    Parses and executes a tool call like 'simulate_impact(node_id="Router-14", ...)'
    Returns the tool output.
    """
    if not tool_call_str:
        return None
    
    try:
        # Simple regex to extract function name and args
        match = re.match(r"(\w+)\((.*)\)", tool_call_str)
        if not match:
            return None
        
        func_name = match.group(1)
        args_str = match.group(2)
        
        # Super simple kwarg parser for the demo
        kwargs = {}
        for arg in args_str.split(','):
            if '=' in arg:
                k, v = arg.split('=')
                kwargs[k.strip()] = v.strip().strip("'").strip('"')
        
        if func_name in TOOLS:
            logger.info(f"⚡ Executing Agent Tool: {func_name}")
            return TOOLS[func_name](**kwargs)
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
    return None

def trigger_agent_pipeline(anomaly_event: dict) -> dict:
    """
    NO-BS Agentic Pipeline:
    1. Retrieval -> Initial Diagnosis (Reasoning)
    2. Tool Execution (Simulation/Query) -> Re-Diagnosis (Refinement)
    3. Action Planning (Command) -> Mitigation Execution
    4. Communication
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    # Step 1: Grounding
    experience = retrieve_experience(str(anomaly_event))
    pattern = memory.detect_pattern()
    context = memory.get_context()

    # Step 2: Initial Predictive Reasoning
    logger.info("🩺 Agent 1: Initial Reasoning...")
    diagnosis = run_diagnosis(anomaly_event, context, pattern, experience)

    # Step 3: Tool Use Loop (The "Moment of Truth")
    tool_output = None
    if diagnosis.get("tool_call"):
        tool_output = execute_agent_tool(diagnosis["tool_call"])
        if tool_output:
            logger.info("🔬 Agent 1: Refining diagnosis with simulation results...")
            diagnosis = run_diagnosis(anomaly_event, context, pattern, experience, tool_output=tool_output)

    # Step 4: Intervention & Automatic Action
    logger.info("🔧 Agent 2: Planning Tactical Intervention...")
    recommendation = run_recommendation(anomaly_event, diagnosis, context, pattern)
    
    # Execute any recommended tools (e.g. mitigation)
    action_results = []
    for action in recommendation.get("actions", []):
        if action.get("tool"):
            res = execute_agent_tool(f"{action['tool']}(action='{action['action']}', target='{diagnosis['predicted_next_failure']}')")
            if res:
                action_results.append(res)

    # Step 5: Crisis Communication
    logger.info("📢 Agent 3: Generating Final Briefing...")
    explanation = run_explanation(anomaly_event, diagnosis, recommendation, context, pattern)

    result = {
        **anomaly_event,
        "pattern_detection": pattern,
        "grounded_experience": experience,
        "simulation_results": tool_output,
        "mitigation_results": action_results,
        "agents": {
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
        "memory": memory.history,
    }
    
    memory.add(result)
    return result
