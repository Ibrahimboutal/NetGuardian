from .gemma_client import query_gemma


def run_recommendation(anomaly_event: dict, diagnosis: dict, context: str = "", pattern: str = "") -> dict:
    """
    Command Agent — Plans tactical interventions and tool use.
    """
    prompt = f"""SYSTEM: You are the Incident Commander for Infrastructure Defense.
Your role is to plan high-impact tactical interventions based on predictive reasoning.
Output strictly valid JSON. No conversational text.

PREDICTIVE DIAGNOSIS:
{diagnosis}

TELEMETRY:
{anomaly_event}

TEMPORAL PATTERN:
{pattern}

JSON SCHEMA:
{{
  "decision": "Short title of the tactical decision",
  "actions": [
    {{ 
      "action": "Description", 
      "priority": "CRITICAL/HIGH/MEDIUM", 
      "tool": "Optional tool name to execute" 
    }}
  ],
  "estimated_recovery_impact": "How this prevents the cascade"
}}

STRICT CONSTRAINT: If the risk is 'CRITICAL' and pattern is 'CASCADING', prioritize isolation tools."""

    required_keys = ["decision", "actions"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Fallback
    if "error" in result:
        return {
            "decision": "Manual Emergency Override",
            "actions": [
                { "action": "Initiate manual node isolation", "priority": "CRITICAL", "tool": "execute_mitigation" }
            ],
            "estimated_recovery_impact": "Prevents immediate cascade propagation via manual isolation."
        }
        
    return result
