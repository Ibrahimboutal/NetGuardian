import logging
from backend.agents.diagnosis_agent import run_diagnosis
from backend.agents.recommendation_agent import run_recommendation
from backend.agents.explanation_agent import run_explanation

logger = logging.getLogger(__name__)

class AnomalyMemory:
    """Enterprise-grade store for incident history and pattern detection."""
    def __init__(self, limit=5):
        self.history = []
        self.limit = limit

    def add(self, event: dict):
        summary = {
            "timestamp": event.get("timestamp"),
            "issue": event.get("agents", {}).get("diagnosis", {}).get("issue", "Unknown"),
            "severity": event.get("severity")
        }
        self.history.insert(0, summary)
        self.history = self.history[:self.limit]

    def detect_pattern(self) -> str:
        """
        WOW FEATURE: Analyzes the last 3 events to detect escalating failures.
        Example: Latency Spike -> Packet Loss -> Node Failure
        """
        if len(self.history) < 2:
            return "Stable / Baseline establishing."
            
        recent = self.history[:3]
        issues = [h['issue'].lower() for h in recent]
        
        # Heuristic for cascading failure
        if any("spike" in i for i in issues) and any("loss" in i or "drop" in i for i in issues):
            return "ALERT: Cascading Failure Pattern Detected (Escalation from Spikes to Packet Drops)."
            
        if len(set(issues)) == 1 and len(issues) >= 3:
            return "WARNING: Persistent / Sustained Incident Pattern."
            
        return "Active / Independent events."

    def get_context(self) -> str:
        if not self.history:
            return "[]"
        import json
        return json.dumps(self.history, indent=2)

# Initialize memory
memory = AnomalyMemory()

def trigger_agent_pipeline(anomaly_event: dict) -> dict:
    """
    Event Bus — orchestrates the 3-agent pipeline with pattern awareness.
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    # Step 1: Detect temporal patterns
    pattern = memory.detect_pattern()
    context = memory.get_context()
    
    logger.info("🩺 Running Specialized Diagnosis Agent...")
    diagnosis = run_diagnosis(anomaly_event, context, pattern)

    logger.info("🔧 Running Specialized Recommendation Agent...")
    recommendation = run_recommendation(anomaly_event, diagnosis, context, pattern)

    logger.info("📢 Running Specialized Explanation Agent...")
    explanation = run_explanation(anomaly_event, diagnosis, recommendation, context, pattern)

    result = {
        **anomaly_event,
        "pattern_detection": pattern,
        "agents": {
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
        "memory": memory.history,
    }
    
    # Save to memory for next time
    memory.add(result)
    
    return result
