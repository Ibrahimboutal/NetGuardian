from .gemma_client import query_gemma


def run_explanation(anomaly_event: dict, diagnosis: str, recommendation: str) -> str:
    """
    Explanation Agent — synthesises everything into a clear, human-readable summary
    for display on the operations dashboard.
    Input:  anomaly + diagnosis + recommendation
    Output: structured markdown-ready explanation
    """
    prompt = f"""You are a network incident communicator writing a dashboard alert.

INCIDENT DATA:
- Time: {anomaly_event['timestamp']}
- Severity: {anomaly_event['severity'].upper()}
- Primary Issue: {anomaly_event['primary_metric']} deviation
- Latency: {anomaly_event['latency_ms']}ms | Packet Loss: {anomaly_event['packet_loss_pct']}% | Throughput: {anomaly_event['throughput_mbps']} Mbps

DIAGNOSIS:
{diagnosis}

RECOMMENDED ACTIONS:
{recommendation}

Write a clear, concise incident summary (3-4 sentences max) for a NOC operator.
Start with the severity and impact. End with the immediate next step.
Use plain language — no jargon beyond standard networking terms."""

    return query_gemma(prompt)
