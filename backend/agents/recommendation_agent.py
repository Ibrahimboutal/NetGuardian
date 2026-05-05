from .gemma_client import query_gemma


def run_recommendation(anomaly_event: dict, diagnosis: dict, context: str = "") -> dict:
    """
    Recommendation Agent — Incident Commander Role.
    Returns: JSON {actions: [{action, priority, difficulty}]}
    """
    prompt = f"""SYSTEM: You are the Incident Commander for Infrastructure Defense.
Your role is to provide immediate, high-impact tactical remediations.
Output strictly valid JSON. No conversational text, no preamble, no fluff.

DIAGNOSIS:
{diagnosis}

TELEMETRY:
{anomaly_event}

HISTORICAL CONTEXT:
{context}

JSON SCHEMA:
{{
  "actions": [
    {{ 
      "action": "Immediate tactical command", 
      "priority": "CRITICAL/HIGH/MEDIUM/LOW", 
      "difficulty": "Easy/Medium/Hard" 
    }}
  ]
}}

STRICT CONSTRAINT: Provide exactly 4 prioritized actions. Be direct, authoritative, and purely actionable. No fluff."""

    return query_gemma(prompt)
