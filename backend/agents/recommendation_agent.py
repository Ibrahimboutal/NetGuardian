from .gemma_client import query_gemma


def run_recommendation(anomaly_event: dict, diagnosis: dict, context: str = "", pattern: str = "") -> dict:
    """
    Command Agent — Plans tactical interventions with trade-off analysis.
    """
    prompt = f"""SYSTEM: You are the Incident Commander for Infrastructure Defense.
Your role is to plan tactical interventions, balancing risk mitigation against service availability.
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
  "trade_off_analysis": "Explicitly weigh the pros and cons of this decision (e.g. Isolation saves network but cuts regional service).",
  "estimated_recovery_impact": "How this prevents the cascade"
}}

STRICT CONSTRAINT: You must explicitly address the TRADE-OFFS of your chosen actions."""

    required_keys = ["decision", "actions", "trade_off_analysis"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Fallback
    if "error" in result:
        return {
            "decision": "Manual Emergency Override",
            "actions": [
                { "action": "Initiate manual node isolation", "priority": "CRITICAL", "tool": "execute_mitigation" }
            ],
            "trade_off_analysis": "Isolation prevents total network collapse at the cost of immediate localized service blackout.",
            "estimated_recovery_impact": "Prevents immediate cascade propagation via manual isolation."
        }
        
    return result
