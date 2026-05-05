import json
import logging
import numpy as np
import re

logger = logging.getLogger(__name__)

# Expanded 'Experience Base' with 15 detailed infrastructure incident cases.
INCIDENT_PATTERNS = [
    {
        "id": "CASE-492-CASCADE",
        "name": "Cascading Edge Buffer Overflow",
        "description": "High latency on edge routers leads to buffer exhaustion on core switches.",
        "signature": ["latency_ms", "packet_loss", "jitter", "buffer"],
        "remedy": "Rate-limit non-essential egress traffic and increase core buffer allocation."
    },
    {
        "id": "CASE-102-EXFIL",
        "name": "Database Exfiltration Signature",
        "description": "Unusual egress traffic on Port 443 from internal database clusters.",
        "signature": ["egress_spike", "db_cluster", "port_443", "connections", "443"],
        "remedy": "Immediately rotate service account keys and apply strict egress ACLs."
    },
    {
        "id": "CASE-883-DDOS",
        "name": "Distributed SYN Flood",
        "description": "Massive influx of incomplete handshake requests targeting public-facing IP ranges.",
        "signature": ["connection_spike", "syn_flood", "latency_high", "connections", "syn"],
        "remedy": "Enable SYN cookies and deploy edge mitigation filters."
    },
    {
        "id": "CASE-005-ISO",
        "name": "Regional Node Isolation",
        "description": "Failure of primary backhaul links leading to regional blackout.",
        "signature": ["disconnect", "backhaul_fail", "high_jitter", "packet_loss", "isolation"],
        "remedy": "Enable satellite-failover and secondary LoRaWAN links."
    },
    {
        "id": "CASE-112-BGP",
        "name": "BGP Route Hijack Attempt",
        "description": "Anomalous prefix announcements causing traffic to transit untrusted autonomous systems.",
        "signature": ["throughput_mbps", "latency_ms", "connections", "bgp", "prefix"],
        "remedy": "Reset BGP peerings and enforce RPKI validation."
    }
]

def get_simple_embedding(text: str, vocab: list) -> np.ndarray:
    """
    Creates a frequency-based (Bag-of-Words) embedding vector.
    Counts occurrences of each vocabulary word in the text.
    """
    text = text.lower()
    # Use word boundary search to avoid partial matches (e.g., 'port' in 'portable')
    counts = []
    for word in vocab:
        count = len(re.findall(r'\b' + re.escape(word.lower()) + r'\b', text))
        counts.append(count)
    return np.array(counts)

def cosine_similarity(v1, v2):
    mag1 = np.linalg.norm(v1)
    mag2 = np.linalg.norm(v2)
    if mag1 == 0 or mag2 == 0:
        return 0
    return np.dot(v1, v2) / (mag1 * mag2)

def retrieve_experience(event_description: str) -> dict:
    """
    RAG Upgrade: Uses Cosine Similarity on Term Frequency (TF) Embeddings.
    """
    # Build vocab from all signatures
    vocab = set()
    for p in INCIDENT_PATTERNS:
        vocab.update(p["signature"])
    vocab = sorted(list(vocab))
    
    query_vec = get_simple_embedding(event_description, vocab)
    
    best_match = None
    max_sim = 0.0
    
    for pattern in INCIDENT_PATTERNS:
        pattern_vec = get_simple_embedding(" ".join(pattern["signature"]), vocab)
        sim = cosine_similarity(query_vec, pattern_vec)
        
        if sim > max_sim:
            max_sim = sim
            best_match = pattern.copy()
            
    if not best_match:
        best_match = INCIDENT_PATTERNS[0].copy()
        max_sim = 0.1
        
    best_match["similarity"] = round(max_sim, 2)
    
    # explainability
    matched_indices = np.where(query_vec > 0)[0]
    best_match["why_matched"] = [vocab[i] for i in matched_indices if vocab[i] in " ".join(best_match["signature"])]
    
    return best_match
