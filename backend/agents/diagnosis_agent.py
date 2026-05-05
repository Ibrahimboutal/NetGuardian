from .gemma_client import query_gemma


def run_diagnosis(anomaly_event: dict) -> str:
    """
    Diagnosis Agent — answers: what is happening right now?
    Input:  anomaly event dict
    Output: plain-text diagnosis string
    """
    prompt = f"""You are a senior network reliability engineer.

An anomaly has been detected in the network with the following metrics:
- Latency: {anomaly_event['latency_ms']}ms  (normal: ~13ms)
- Throughput: {anomaly_event['throughput_mbps']} Mbps  (normal: ~950 Mbps)
- Packet Loss: {anomaly_event['packet_loss_pct']}%  (normal: ~0.1%)
- Jitter: {anomaly_event['jitter_ms']}ms  (normal: ~2ms)
- Active Connections: {anomaly_event['connections']}  (normal: ~141)
- Severity: {anomaly_event['severity'].upper()}
- Primary Metric: {anomaly_event['primary_metric']}
- Timestamp: {anomaly_event['timestamp']}

In 2-3 sentences, explain clearly and concisely:
1. What is happening in the network right now?
2. What are the most likely root causes?

Be specific and technical. Do NOT suggest actions yet."""

    return query_gemma(prompt)
