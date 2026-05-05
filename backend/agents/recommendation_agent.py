from .gemma_client import query_gemma


def run_recommendation(anomaly_event: dict, diagnosis: str) -> str:
    """
    Recommendation Agent — answers: what should we do about it?
    Input:  anomaly event + diagnosis text
    Output: numbered action list
    """
    prompt = f"""You are a network operations expert.

SITUATION:
{diagnosis}

CURRENT METRICS:
- Latency: {anomaly_event['latency_ms']}ms
- Packet Loss: {anomaly_event['packet_loss_pct']}%
- Throughput: {anomaly_event['throughput_mbps']} Mbps
- Jitter: {anomaly_event['jitter_ms']}ms
- Severity: {anomaly_event['severity'].upper()}

Provide exactly 4 concrete remediation actions, numbered 1-4.
Each action must be specific and immediately actionable.
Format: "1. [Action]" — one action per line.
Do NOT repeat the diagnosis. Focus only on actions."""

    return query_gemma(prompt)
