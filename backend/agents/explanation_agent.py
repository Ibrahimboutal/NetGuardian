from .gemma_client import query_gemma


def run_explanation(anomaly_event: dict, diagnosis: dict, recommendation: dict, context: str = "", pattern: str = "") -> dict:
    """
    Communicator Agent — Briefs stakeholders on predictions and actions.
    """
    prompt = f"""SYSTEM: You are the Crisis Communicator for the Network Operations Center.
Your role is to brief stakeholders on intercepted failures and tactical status.
Output strictly valid JSON. No conversational text.

PREDICTIONS:
{diagnosis}

TACTICAL ACTIONS:
{recommendation}

JSON SCHEMA:
{{
  "summary": "Briefing on the predicted incident and the prevention measures taken",
  "eta_guess": "Current containment status",
  "status_color": "red/yellow/green"
}}

STRICT CONSTRAINT: Focus on how the system PREVENTED a larger failure through proactive reasoning."""

    required_keys = ["summary", "status_color"]
    result = query_gemma(prompt, required_keys=required_keys)
    
    # Fallback
    if "error" in result:
        return {
            "summary": "NetGuardian has detected and is mitigating a high-risk system event. Proactive containment protocols are active to protect critical infrastructure.",
            "eta_guess": "Mitigation in progress.",
            "status_color": "red"
        }
        
    return result
