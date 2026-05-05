from .gemma_client import query_gemma


def run_explanation(anomaly_event: dict, diagnosis: dict, recommendation: dict, context: str = "") -> dict:
    """
    Explanation Agent — Crisis Communicator Role.
    Returns: JSON {summary, eta_guess, status_color}
    """
    prompt = f"""SYSTEM: You are the Crisis Communicator for the Network Operations Center.
Your role is to translate technical findings into a professional narrative for stakeholders.
Output strictly valid JSON. No conversational text, no preamble, no fluff.

DIAGNOSIS:
{diagnosis}

RECOMMENDED ACTIONS:
{recommendation}

HISTORICAL CONTEXT:
{context}

JSON SCHEMA:
{{
  "summary": "Professional narrative summary explaining what happened and what we are doing",
  "eta_guess": "Expected time to mitigation or containment",
  "status_color": "red (critical) / yellow (degraded) / green (stable)"
}}

STRICT CONSTRAINT: Use a professional, calm, yet urgent narrative style. Avoid excessive jargon in the summary."""

    result = query_gemma(prompt)
    
    # Failure handling
    if "error" in result or not result.get("summary"):
        return {
            "summary": "We are currently observing anomalous system behavior. Detailed AI analysis is currently degraded, but automated containment protocols remain active.",
            "eta_guess": "Unknown",
            "status_color": "yellow"
        }
        
    return result
