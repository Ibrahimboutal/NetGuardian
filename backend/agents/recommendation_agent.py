from .gemma_client import query_gemma


def run_recommendation(anomaly_event: dict, diagnosis: dict, context: str = "") -> dict:
    """
    Command Agent — Tactical Decision Making.
    Selects from a sophisticated mitigation toolset based on trade-off analysis.
    """
    prompt = f"""SYSTEM: You are the Tactical Incident Commander for Network Defense.
Your goal is to neutralize the threat while maintaining maximum uptime.

DIAGNOSIS EVIDENCE:
{diagnosis}

INCIDENT CONTEXT:
{context}

AVAILABLE TACTICAL TOOLS:
1. `throttle_traffic(node_id, pct)`: Best for DDoS or buffer exhaustion. Minimal service impact.
2. `reroute_path(source, blocked)`: Best for link degradation or local outages. Zero traffic loss if redundant paths exist.
3. `execute_mitigation(action, target)`: Use for 'Isolate' (Extreme safety) or 'Failover' (High availability).

STRICT OUTPUT CONSTRAINTS:
1. You MUST choose the tool that minimizes service loss while guaranteeing containment.
2. Provide a 'Strategic Justification' explaining why you chose one tool over another.
3. Output strictly valid JSON.

JSON SCHEMA:
{{
  "decision": "Intervention Strategy",
  "actions": [
    {{ "action": "Step description", "tool": "tool_name", "priority": "HIGH" }}
  ],
  "strategic_justification": "Why this specific tool? (e.g., Throttling preferred over isolation to keep 80% traffic alive)",
  "trade_off": "Availability cost of this decision"
}}"""

    result = query_gemma(prompt)
    
    if "error" in result:
        return {
            "decision": "Emergency Isolation",
            "actions": [{"action": "Isolate Node", "tool": "execute_mitigation", "priority": "CRITICAL"}],
            "strategic_justification": "Immediate isolation required to stop cascade propagation.",
            "trade_off": "100% loss for the target node."
        }
        
    return result
