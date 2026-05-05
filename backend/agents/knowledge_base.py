import json
import logging

logger = logging.getLogger(__name__)

# A simple "Experience Base" of known failure patterns for critical infrastructure.
INCIDENT_PATTERNS = [
    {
        "id": "CASE-492-CASCADE",
        "name": "Cascading Edge Buffer Overflow",
        "description": "High latency on edge routers leads to buffer exhaustion on core switches, resulting in packet drops.",
        "signature": ["latency_ms", "packet_loss", "jitter"],
        "remedy": "Rate-limit non-essential egress traffic and increase core buffer allocation."
    },
    {
        "id": "CASE-102-EXFIL",
        "name": "Database Exfiltration Signature",
        "description": "Unusual egress traffic on Port 443 from internal database clusters, often following a credential spray attempt.",
        "signature": ["egress_spike", "db_cluster", "port_443", "connections"],
        "remedy": "Immediately rotate service account keys and apply strict egress ACLs to DB VLAN."
    },
    {
        "id": "CASE-883-DDOS",
        "name": "Distributed SYN Flood",
        "description": "Massive influx of incomplete handshake requests targeting public-facing IP ranges.",
        "signature": ["connection_spike", "syn_flood", "latency_high", "connections"],
        "remedy": "Enable SYN cookies and deploy edge mitigation filters via upstream ISP."
    },
    {
        "id": "CASE-005-ISO",
        "name": "Regional Node Isolation",
        "description": "Failure of primary and secondary backhaul links leading to total regional blackout.",
        "signature": ["disconnect", "backhaul_fail", "high_jitter", "packet_loss"],
        "remedy": "Enable satellite-failover and reroute critical telemetry through secondary LoRaWAN links."
    }
]

def retrieve_experience(event_description: str) -> dict:
    """
    Simple keyword-based retrieval with explicit similarity scoring.
    """
    event_lower = event_description.lower()
    best_match = None
    max_score = 0.0
    
    for pattern in INCIDENT_PATTERNS:
        matches = sum(1 for tag in pattern["signature"] if tag in event_lower)
        score = matches / len(pattern["signature"]) if pattern["signature"] else 0
        
        if score > max_score:
            max_score = score
            best_match = pattern.copy()
            best_match["similarity"] = round(score, 2)
            
    if not best_match:
        best_match = INCIDENT_PATTERNS[0].copy()
        best_match["similarity"] = 0.1
        
    return best_match
