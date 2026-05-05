from .gemma_client import query_gemma


def run_recommendation(anomaly_event: dict, diagnosis: dict, context: str = "", pattern: str = "") -> dict:
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

TEMPORAL PATTERN DETECTION:
{pattern}

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

STRICT CONSTRAINT: 
1. Think step-by-step: assess the pattern, prioritize based on severity, then select remediations.
2. If the pattern is 'CASCADING', prioritize isolation over recovery.
3. Provide exactly 4 prioritized actions. Be direct, authoritative, and purely actionable."""

    required_keys = ["actions"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Failure handling
    if "error" in result:
        return {
            "actions": [
                { "action": "EMERGENCY: Isolate affected nodes (AI Validation Failed)", "priority": "CRITICAL", "difficulty": "Easy" },
                { "action": "Initiate snapshot and forensic dump", "priority": "HIGH", "difficulty": "Medium" },
                { "action": "Consult emergency runbooks", "priority": "HIGH", "difficulty": "Medium" },
                { "action": "Manual audit of recent telemetry", "priority": "MEDIUM", "difficulty": "Hard" }
            ]
        }
        
    return result
