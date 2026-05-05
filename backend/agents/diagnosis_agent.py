from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "", experience: dict = None, tool_output: dict = None) -> dict:
    """
    Reasoning Agent — Probabilistic Failure Prediction.
    Outputs multiple hypotheses with confidence levels.
    """
    simulation_section = f"\nLIVE SIMULATION RESULTS:\n{tool_output}" if tool_output else ""

    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst for Critical Infrastructure.
Your role is to perform PROBABILISTIC reasoning and PREDICT cascading failures.
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
  "hypotheses": [
    {{ "node": "Router-14", "confidence": 0.65, "reasoning": "Observed buffer pressure" }},
    {{ "node": "Switch-02", "confidence": 0.25, "reasoning": "Secondary downstream link" }}
  ],
  "predicted_next_failure": "Primary node from highest confidence hypothesis",
  "probability_of_cascade": "Value between 0 and 1",
  "confidence": "Your total confidence in this diagnosis",
  "reasoning_trace": "Step-by-step logic",
  "tool_call": "Optional: simulate_impact(node_id='...')",
  "needs_more_analysis": "True/False - set to True if simulation results are ambiguous"
}}

STRICT CONSTRAINT: 
1. Provide at least TWO hypotheses with different confidence levels.
2. Use 'needs_more_analysis' if you believe a second simulation pass is required.
3. Think step-by-step. Focus on the DELTA between initial telemetry and simulation data."""

    required_keys = ["risk_level", "hypotheses", "reasoning_trace"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Fallback
    if "error" in result:
        return {
            "risk_level": "HIGH",
            "hypotheses": [
                { "node": "Router-14 (Edge)", "confidence": 0.70, "reasoning": "Direct telemetry correlation" },
                { "node": "Core-Switch-01", "confidence": 0.20, "reasoning": "Upstream propagation path" }
            ],
            "predicted_next_failure": "Router-14 (Edge)",
            "probability_of_cascade": 0.5,
            "confidence": 0.3,
            "reasoning_trace": "AI reasoning failed to generate valid structured trace.",
            "tool_call": None,
            "needs_more_analysis": False
        }
    
    return result
