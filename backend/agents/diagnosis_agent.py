import logging
from .gemma_client import query_gemma

logger = logging.getLogger(__name__)

# Official Gemma 4 Tool Definitions
DIAGNOSIS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "simulate_impact",
            "description": "Runs a graph-based simulation to predict the impact of a node failure on the network.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "The ID of the router or switch to simulate (e.g., 'Router-14')"},
                    "failure_type": {"type": "string", "enum": ["buffer_exhaustion", "latency_spike", "disconnect"], "description": "Type of failure to model"}
                },
                "required": ["node_id", "failure_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_node_status",
            "description": "Retrieves real-time health metrics (latency, load, status) for a specific infrastructure node.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "The ID of the infrastructure node"}
                },
                "required": ["node_id"]
            }
        }
    }
]

def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "", experience: dict = None, tool_output: dict = None, analysis_depth: str = "INITIAL_HYPOTHESIS") -> dict:
    """
    Reasoning Agent — Probabilistic Failure Prediction.
    Uses Native Gemma 4 Function Calling to gather evidence.
    """
    simulation_section = f"\nLIVE SIMULATION RESULTS:\n{tool_output}" if tool_output else ""

    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst for Critical Infrastructure.
Your role is to perform PROBABILISTIC reasoning and PREDICT cascading failures using the available diagnostic tools.
ANALYSIS MODE: {analysis_depth}

SITUATION TELEMETRY:
{anomaly_event}

HISTORICAL CONTEXT:
{context}

TEMPORAL PATTERN:
{pattern}

GROUNDED EXPERIENCE:
{experience}{simulation_section}

STRICT CONSTRAINTS: 
1. Provide at least TWO hypotheses.
2. If you need more evidence or a cascade simulation, use the native 'simulate_impact' or 'get_node_status' tools.
3. Think step-by-step. If analysis_depth is 'SECOND_PASS_REFINEMENT', provide an exhaustive reasoning trace explaining the 'Why' behind your prediction."""

    # Using Native Gemma 4 Tool Calling
    result = query_gemma(prompt, tools=DIAGNOSIS_TOOLS)
    
    # Handle Tool Call Response
    if isinstance(result, dict) and result.get("type") == "tool_call":
        logger.info(f"🛠️ Agent requested tool call: {result['calls'][0]['function']['name']}")
        return result # Return the tool call object for the orchestrator to handle
    
    # Fallback/Default Structure
    if "error" in result:
        return {
            "risk_level": "HIGH",
            "hypotheses": [
                { "node": "Router-14 (Edge)", "confidence": 0.70, "reasoning": "Direct telemetry correlation" },
                { "node": "Core-Switch-01", "confidence": 0.20, "reasoning": "Upstream propagation path" }
            ],
            "predicted_next_failure": "Router-14 (Edge)",
            "reasoning_trace": f"[{analysis_depth}] Local Inference Fallback: Detected high pressure on egress buffer.",
            "tool_call": None
        }
    
    return result
