import json
import logging

logger = logging.getLogger(__name__)

# Expanded 'Experience Base' with 15 detailed infrastructure incident cases.
INCIDENT_PATTERNS = [
    {
        "id": "CASE-492-CASCADE",
        "name": "Cascading Edge Buffer Overflow",
        "description": "High latency on edge routers leads to buffer exhaustion on core switches.",
        "signature": ["latency_ms", "packet_loss", "jitter"],
        "remedy": "Rate-limit non-essential egress traffic and increase core buffer allocation."
    },
    {
        "id": "CASE-102-EXFIL",
        "name": "Database Exfiltration Signature",
        "description": "Unusual egress traffic on Port 443 from internal database clusters.",
        "signature": ["egress_spike", "db_cluster", "port_443", "connections"],
        "remedy": "Immediately rotate service account keys and apply strict egress ACLs."
    },
    {
        "id": "CASE-883-DDOS",
        "name": "Distributed SYN Flood",
        "description": "Massive influx of incomplete handshake requests targeting public-facing IP ranges.",
        "signature": ["connection_spike", "syn_flood", "latency_high", "connections"],
        "remedy": "Enable SYN cookies and deploy edge mitigation filters."
    },
    {
        "id": "CASE-005-ISO",
        "name": "Regional Node Isolation",
        "description": "Failure of primary backhaul links leading to regional blackout.",
        "signature": ["disconnect", "backhaul_fail", "high_jitter", "packet_loss"],
        "remedy": "Enable satellite-failover and secondary LoRaWAN links."
    },
    {
        "id": "CASE-112-BGP",
        "name": "BGP Route Hijack Attempt",
        "description": "Anomalous prefix announcements causing traffic to transit untrusted autonomous systems.",
        "signature": ["throughput_mbps", "latency_ms", "connections"],
        "remedy": "Reset BGP peerings and enforce RPKI validation."
    },
    {
        "id": "CASE-221-THERMAL",
        "name": "Critical Thermal Throttling",
        "description": "Environmental sensor failure leading to hardware CPU throttling and jitter spikes.",
        "signature": ["jitter_ms", "latency_ms", "throughput_mbps"],
        "remedy": "Automated migration of critical VMs and activation of secondary cooling."
    },
    {
        "id": "CASE-334-DNS",
        "name": "Internal DNS Amplification",
        "description": "High volume of recursive DNS queries originating from compromised IoT subnet.",
        "signature": ["throughput_mbps", "connections", "latency_ms"],
        "remedy": "Isolate IoT subnet and deploy DNS rate-limiting."
    },
    {
        "id": "CASE-445-FIRM",
        "name": "Faulty Firmware Rollout",
        "description": "Widespread packet drops following a distributed firmware update on Layer 2 switches.",
        "signature": ["packet_loss_pct", "jitter_ms"],
        "remedy": "Rollback firmware to previous stable version (v12.4.2)."
    },
    {
        "id": "CASE-556-SCADA",
        "name": "SCADA Protocol Anomalies",
        "description": "Unauthorized Modbus/TCP write commands detected targeting power distribution units.",
        "signature": ["connections", "throughput_mbps", "latency_ms"],
        "remedy": "Activate SCADA air-gap protocols and initiate forensic log capture."
    },
    {
        "id": "CASE-667-STORM",
        "name": "Multicast Broadcast Storm",
        "description": "Switch loop causing exponential increase in broadcast traffic and CPU exhaustion.",
        "signature": ["throughput_mbps", "latency_ms", "packet_loss_pct"],
        "remedy": "Enable spanning-tree BPDU guard and isolate faulty VLAN."
    },
    {
        "id": "CASE-778-VLAN",
        "name": "VLAN Hopping Intrusion",
        "description": "Attacker attempting to bypass network segmentation via double-tagging.",
        "signature": ["connections", "throughput_mbps", "jitter_ms"],
        "remedy": "Disable dynamic trunking protocol (DTP) and prune unused VLANs."
    },
    {
        "id": "CASE-889-RAT",
        "name": "Encrypted RAT Beaconing",
        "description": "Periodic low-volume heartbeats detected from core engineering workstations.",
        "signature": ["connections", "latency_ms", "throughput_mbps"],
        "remedy": "Quarantine workstation and initiate deep packet inspection."
    },
    {
        "id": "CASE-990-DHCP",
        "name": "Rogue DHCP Server Discovery",
        "description": "Unauthorized DHCP offers causing IP address conflicts and traffic redirection.",
        "signature": ["connections", "latency_ms", "packet_loss_pct"],
        "remedy": "Enable DHCP snooping and block rogue port."
    },
    {
        "id": "CASE-011-ARP",
        "name": "Man-in-the-Middle ARP Spoof",
        "description": "Gratuitous ARP replies mapping sensitive gateways to untrusted MAC addresses.",
        "signature": ["latency_ms", "jitter_ms", "packet_loss_pct"],
        "remedy": "Enable dynamic ARP inspection (DAI) and static MAC binding."
    },
    {
        "id": "CASE-022-POWER",
        "name": "Edge Site Power Oscillation",
        "description": "Unstable power input causing edge router reboots and packet bursts.",
        "signature": ["packet_loss_pct", "jitter_ms", "throughput_mbps"],
        "remedy": "Switch site to battery backup and initiate maintenance ticket."
    }
]

def retrieve_experience(event_description: str) -> dict:
    """
    Enhanced retrieval with explainability (why_matched).
    """
    event_lower = event_description.lower()
    best_match = None
    max_score = 0.0
    matched_tags = []
    
    for pattern in INCIDENT_PATTERNS:
        current_matched = [tag for tag in pattern["signature"] if tag in event_lower]
        score = len(current_matched) / len(pattern["signature"]) if pattern["signature"] else 0
        
        if score > max_score:
            max_score = score
            best_match = pattern.copy()
            matched_tags = current_matched
            
    if not best_match:
        best_match = INCIDENT_PATTERNS[0].copy()
        best_match["similarity"] = 0.1
        best_match["why_matched"] = ["General Anomaly Pattern"]
    else:
        best_match["similarity"] = round(max_score, 2)
        best_match["why_matched"] = matched_tags
        
    return best_match
