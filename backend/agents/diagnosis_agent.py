from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict, context: str = "", pattern: str = "") -> dict:
    """
    Diagnosis Agent — Technical Analyst Role.
    Returns: JSON {issue, root_cause, confidence, impact}
    """
    prompt = f"""SYSTEM: You are the Lead Network Forensic Analyst for Critical Infrastructure.
Your role is to perform deep technical analysis of anomalous network events.
Output strictly valid JSON. No conversational text, no preamble, no fluff.

SITUATION TELEMETRY:
{anomaly_event}

HISTORICAL CONTEXT (Past 5 Incidents):
{context}

TEMPORAL PATTERN DETECTION:
{pattern}

JSON SCHEMA:
{{
  "issue": "Technical classification of the incident",
  "root_cause": "Detailed technical root cause",
  "confidence": "Analysis confidence percentage (e.g. 95%)",
  "impact": "Operational impact on critical systems"
}}

STRICT CONSTRAINT: 
1. Think step-by-step internally: first classify, then infer root cause, then estimate impact.
2. Use the 'TEMPORAL PATTERN' to determine if this is a recurring or cascading issue.
3. Maintain a clinical, analytical, and highly technical tone."""

    required_keys = ["issue", "root_cause", "confidence", "impact"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Failure handling for bad outputs
    if "error" in result:
        return {
            "issue": "Analysis Degraded",
            "root_cause": f"Model output validation failed ({result['error']})",
            "confidence": "Low",
            "impact": "Manual verification required. Potential hidden cascading failure."
        }
    
    return result
