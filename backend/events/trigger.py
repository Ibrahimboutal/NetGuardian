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

    def detect_pattern(self) -> dict:
        if len(self.history) < 2:
            return {"pattern": "Stable / Baseline establishing.", "confidence": 1.0}
        
        recent = self.history[:3]
        issues = [h['issue'].lower() for h in recent]
        
        if any("spike" in i for i in issues) and any("loss" in i or "drop" in i for i in issues):
            return {
                "pattern": "ALERT: Cascading Failure Pattern Detected.",
                "confidence": 0.82
            }
        
        if len(set(issues)) == 1 and len(issues) >= 3:
            return {
                "pattern": "WARNING: Persistent / Sustained Incident Pattern.",
                "confidence": 0.95
            }
            
        return {"pattern": "Active / Independent events.", "confidence": 0.45}

    def get_context(self) -> str:
        if not self.history:
            return "[]"
        return json.dumps(self.history, indent=2)

# Initialize memory
memory = AnomalyMemory()

def execute_structured_tool(tool_call: dict):
    """
    Executes a structured tool call: {"name": "...", "args": {...}}
    """
    if not tool_call or not isinstance(tool_call, dict):
        return None
    
    name = tool_call.get("name")
    args = tool_call.get("args", {})
    
    if name in TOOLS:
        logger.info(f"⚡ Executing Structured Tool: {name}")
        try:
            return TOOLS[name](**args)
        except Exception as e:
            logger.error(f"Structured tool execution failed: {e}")
    return None

def trigger_agent_pipeline(anomaly_event: dict) -> dict:
    """
    Ultimate Adaptive Pipeline:
    1. Structured Retrieval
    2. Hypothesis Formation (Initial)
    3. Tool Execution & Adaptive Refinement (Second Pass)
    4. Tactical Command & Trade-offs
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    # Step 1: Explainable Retrieval & Memory
    experience = retrieve_experience(str(anomaly_event))
    pattern_data = memory.detect_pattern()
    context = memory.get_context()

    # Step 2: Initial Diagnosis (T1)
    initial_diagnosis = run_diagnosis(anomaly_event, context, str(pattern_data), experience, analysis_depth="INITIAL_HYPOTHESIS")
    initial_confidence = initial_diagnosis.get("confidence", 0.5)

    # Step 3: Tool Execution & Adaptive Pass (T2)
    tool_output = None
    refined_diagnosis = initial_diagnosis
    confidence_delta = 0.0
    adaptive_pass = False

    if initial_diagnosis.get("tool_call"):
        tool_output = execute_structured_tool(initial_diagnosis["tool_call"])
        if tool_output:
            logger.info("🔬 Agent 1: Initiating Adaptive Refinement (Second Pass)...")
            adaptive_pass = True
            refined_diagnosis = run_diagnosis(
                anomaly_event, context, str(pattern_data), experience, 
                tool_output=tool_output, 
                analysis_depth="SECOND_PASS_REFINEMENT"
            )
            confidence_delta = round(float(refined_diagnosis.get("confidence", 0.5)) - float(initial_confidence), 2)

    # Step 4: Tactical Command with Trade-offs
    recommendation = run_recommendation(anomaly_event, refined_diagnosis, context, str(pattern_data))
    
    # Execute mitigation
    action_results = []
    for action in recommendation.get("actions", []):
        if action.get("tool"):
            # Execute mitigation via structured call
            res = execute_structured_tool({
                "name": action["tool"], 
                "args": {"action": action["action"], "target": refined_diagnosis.get("predicted_next_failure", "Unknown")}
            })
            if res:
                action_results.append(res)

    # Step 5: Briefing
    explanation = run_explanation(anomaly_event, refined_diagnosis, recommendation, context, str(pattern_data))

    result = {
        **anomaly_event,
        "belief_evolution": {
            "initial_confidence": initial_confidence,
            "refined_confidence": refined_diagnosis.get("confidence", 0.5),
            "confidence_delta": confidence_delta,
            "adaptive_pass_triggered": adaptive_pass,
            "analysis_depth": refined_diagnosis.get("analysis_depth", "SECOND_PASS" if adaptive_pass else "INITIAL"),
            "tool_used": initial_diagnosis.get("tool_call", {}).get("name") if isinstance(initial_diagnosis.get("tool_call"), dict) else None
        },
        "pattern_intelligence": pattern_data,
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
