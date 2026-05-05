from .gemma_client import query_gemma


def run_explanation(anomaly_event: dict, diagnosis: dict, recommendation: dict, context: str = "", pattern: str = "") -> dict:
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

TEMPORAL PATTERN DETECTION:
{pattern}

JSON SCHEMA:
{{
  "summary": "Professional narrative summary explaining what happened and what we are doing",
  "eta_guess": "Expected time to mitigation or containment",
  "status_color": "red (critical) / yellow (degraded) / green (stable)"
}}

STRICT CONSTRAINT: 
1. Think step-by-step: summarize the event, explain the remediation, then reassure stakeholders.
2. If the pattern is 'CASCADING', emphasize the scale and the urgency of the containment.
3. Use a professional, calm, yet urgent narrative style. Avoid excessive jargon in the summary."""

    required_keys = ["summary", "eta_guess", "status_color"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Failure handling
    if "error" in result:
        return {
            "summary": "We are currently observing anomalous system behavior. Detailed AI analysis is currently degraded, but automated containment protocols remain active. Our team is investigating potential cascading impacts.",
            "eta_guess": "Unknown (Manual Verification Required)",
            "status_color": "yellow"
        }
        
    return result
