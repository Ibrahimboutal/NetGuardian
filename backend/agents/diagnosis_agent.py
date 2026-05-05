from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict, context: str = "") -> dict:
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

JSON SCHEMA:
{{
  "issue": "Technical classification of the incident",
  "root_cause": "Detailed technical root cause",
  "confidence": "Analysis confidence percentage (e.g. 95%)",
  "impact": "Operational impact on critical systems"
}}

STRICT CONSTRAINT: Maintain a clinical, analytical, and highly technical tone."""

    return query_gemma(prompt)
