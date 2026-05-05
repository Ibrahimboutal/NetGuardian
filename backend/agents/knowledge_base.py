import json
import logging

logger = logging.getLogger(__name__)

# A simple "Experience Base" of known failure patterns for critical infrastructure.
# In a real system, this would be a Vector DB.
INCIDENT_PATTERNS = [
    {
        "id": "cascade_01",
        "name": "Cascading Edge Buffer Overflow",
        "description": "High latency on edge routers leads to buffer exhaustion on core switches, resulting in packet drops.",
        "signature": ["latency_spike", "buffer_full", "packet_loss"],
        "remedy": "Rate-limit non-essential egress traffic and increase core buffer allocation."
    },
    {
        "id": "exfil_04",
        "name": "Database Exfiltration Signature",
        "description": "Unusual egress traffic on Port 443 from internal database clusters, often following a credential spray attempt.",
        "signature": ["egress_spike", "db_cluster", "port_443"],
        "remedy": "Immediately rotate service account keys and apply strict egress ACLs to DB VLAN."
    },
    {
        "id": "ddos_syn_flood",
        "name": "Distributed SYN Flood",
        "description": "Massive influx of incomplete handshake requests targeting public-facing IP ranges.",
        "signature": ["connection_spike", "syn_flood", "latency_high"],
        "remedy": "Enable SYN cookies and deploy edge mitigation filters via upstream ISP."
    },
    {
        "id": "node_isolation",
        "name": "Regional Node Isolation",
        "description": "Failure of primary and secondary backhaul links leading to total regional blackout.",
        "signature": ["disconnect", "backhaul_fail", "high_jitter"],
        "remedy": "Enable satellite-failover and reroute critical telemetry through secondary LoRaWAN links."
    }
]

def retrieve_experience(event_description: str) -> dict:
    """
    Simple keyword-based retrieval to ground the AI in past 'Experience'.
    Simulates a Vector DB lookup.
    """
    event_lower = event_description.lower()
    best_match = None
    max_matches = 0
    
    for pattern in INCIDENT_PATTERNS:
        matches = sum(1 for tag in pattern["signature"] if tag in event_lower)
        if matches > max_matches:
            max_matches = matches
            best_match = pattern
            
    return best_match or INCIDENT_PATTERNS[0]  # Fallback to a general pattern
