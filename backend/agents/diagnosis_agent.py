from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "", experience: dict = None, tool_output: dict = None) -> dict:
    """
    Reasoning Agent — Predicts cascades and identifies next failure points.
    Refines analysis if tool_output (simulation) is provided.
    """
    simulation_section = f"\nLIVE SIMULATION RESULTS:\n{tool_output}" if tool_output else ""

    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst for Critical Infrastructure.
Your role is to perform deep technical reasoning and PREDICT cascading failures.
Output strictly valid JSON. No conversational text.

SITUATION TELEMETRY:
{anomaly_event}

HISTORICAL CONTEXT:
{context}

TEMPORAL PATTERN:
{pattern}

GROUNDED EXPERIENCE:
{experience}{simulation_section}

JSON SCHEMA:
{{
  "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
  "predicted_next_failure": "Node or system part likely to fail next",
  "probability_of_cascade": "Value between 0 and 1",
  "confidence": "Your confidence in this prediction",
  "reasoning_trace": "Step-by-step logic",
  "tool_call": "Optional: simulate_impact(node_id='...') if you need more data"
}}

STRICT CONSTRAINT: 
1. If 'LIVE SIMULATION RESULTS' are present, use them to finalize your prediction.
2. If you are unsure, use 'tool_call' to request a simulation."""

    required_keys = ["risk_level", "predicted_next_failure", "reasoning_trace"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Fallback
    if "error" in result:
        return {
            "risk_level": "HIGH",
            "predicted_next_failure": "Unknown (Analysis Degraded)",
            "probability_of_cascade": 0.5,
            "confidence": 0.2,
            "reasoning_trace": "AI reasoning failed to generate valid structured trace.",
            "tool_call": None
        }
    
    return result
