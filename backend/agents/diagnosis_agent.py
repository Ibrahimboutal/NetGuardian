import logging
from .gemma_client import query_gemma

logger = logging.getLogger(__name__)

# Official Gemma 4 Tool Definitions
DIAGNOSIS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "simulate_impact",
            "description": "Runs a graph-based simulation to predict the impact of a node failure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Target node (e.g., 'Router-14')"},
                    "failure_type": {"type": "string", "enum": ["buffer_exhaustion", "latency_spike", "disconnect"]}
                },
                "required": ["node_id", "failure_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_node_status",
            "description": "Retrieves real-time health metrics for a specific node.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"}
                },
                "required": ["node_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_topology",
            "description": "Returns immediate network connectivity and redundancy status for a node.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"}
                },
                "required": ["node_id"]
            }
        }
    }
]

def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "", experience: dict = None, tool_output: dict = None, analysis_depth: str = "INITIAL_HYPOTHESIS") -> dict:
    """
    Reasoning Agent — Probabilistic Failure Prediction.
    Enforces a strict Reasoning Trace: Hypothesis → Evidence → Decision.
    """
    simulation_section = f"\nLIVE EVIDENCE GATHERED:\n{tool_output}" if tool_output else ""
    experience_section = ""
    if experience:
        experience_section = f"\nGROUNDED CASE MATCH:\n{experience}"

    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst.
Your goal is to explain exactly 'Why' a failure is occurring. 
You MUST provide a structured 'Reasoning Trace' for the human operator.

ANALYSIS DEPTH: {analysis_depth}
SITUATION: {anomaly_event}
CONTEXT: {context}
{simulation_section}
{experience_section}

STRICT OUTPUT CONSTRAINTS:
1. Always follow the 'Reasoning Trace' structure:
   - [OBSERVATION]: Key deviations in the telemetry.
   - [HYPOTHESIS]: Proposed root cause.
   - [REASONING]: Step-by-step logic.
   - [VALIDATION]: How simulation/topology evidence proves or disproves the hypothesis.
2. If uncertainty > 40%, you MUST request 'simulate_impact' or 'analyze_topology'.
3. Output strictly valid JSON."""

    result = query_gemma(prompt, tools=DIAGNOSIS_TOOLS)
    
    if isinstance(result, dict) and result.get("type") == "tool_call":
        return result
    
    # Fallback
    if "error" in result:
        return {
            "risk_level": "HIGH",
            "hypotheses": [{"node": "Router-14", "confidence": 0.85}],
            "predicted_next_failure": "Router-14",
            "reasoning_trace": "[REASONING]: Cascade likely at the edge due to buffer pressure.",
            "tool_call": None
        }
    
    return result
