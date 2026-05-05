from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "", experience: dict = None, tool_output: dict = None, analysis_depth: str = "INITIAL_HYPOTHESIS") -> dict:
    """
    Reasoning Agent — Probabilistic Failure Prediction.
    analysis_depth: 'INITIAL_HYPOTHESIS' or 'SECOND_PASS_REFINEMENT'
    """
    simulation_section = f"\nLIVE SIMULATION RESULTS:\n{tool_output}" if tool_output else ""

    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst for Critical Infrastructure.
Your role is to perform PROBABILISTIC reasoning and PREDICT cascading failures.
ANALYSIS MODE: {analysis_depth}

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
  "tool_call": {{
    "name": "simulate_impact",
    "args": {{ "node_id": "Router-14", "failure_type": "buffer_exhaustion" }}
  }},
  "needs_more_analysis": "True/False - set to True if simulation results are ambiguous"
}}

STRICT CONSTRAINT: 
1. Provide at least TWO hypotheses.
2. Use 'tool_call' object if you need more data (name and args).
3. Think step-by-step. If analysis_depth is 'SECOND_PASS_REFINEMENT', provide a much deeper reasoning trace."""

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
            "reasoning_trace": f"[{analysis_depth}] AI reasoning fallback. Simulation grounding suggests escalating buffer pressure.",
            "tool_call": None,
            "needs_more_analysis": False
        }
    
    return result
