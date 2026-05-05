from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "", experience: dict = None) -> dict:
    """
    Reasoning Agent — Predicts cascades and identifies next failure points.
    """
    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst for Critical Infrastructure.
Your role is to perform deep technical reasoning and PREDICT cascading failures.
Output strictly valid JSON. No conversational text.

SITUATION TELEMETRY:
{anomaly_event}

HISTORICAL CONTEXT:
{context}

TEMPORAL PATTERN:
{pattern}

GROUNDED EXPERIENCE (Similar past incident):
{experience}

JSON SCHEMA:
{{
  "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
  "predicted_next_failure": "Node or system part likely to fail next",
  "probability_of_cascade": "Value between 0 and 1",
  "confidence": "Your confidence in this prediction",
  "reasoning_trace": "Step-by-step logic: classify -> infer root cause -> predict next step",
  "tool_call": "Optional: tool_name(args) if you need a simulation"
}}

STRICT CONSTRAINT: Think step-by-step. Focus on PREDICTION, not just description."""

    required_keys = ["risk_level", "predicted_next_failure", "reasoning_trace"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Fallback
    if "error" in result:
        return {
            "risk_level": "HIGH",
            "predicted_next_failure": "Unknown (Analysis Degraded)",
            "probability_of_cascade": 0.5,
            "confidence": 0.2,
            "reasoning_trace": "AI reasoning failed to generate valid structured trace. Falling back to high-risk state.",
            "tool_call": None
        }
    
    return result
