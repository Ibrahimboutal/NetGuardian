import logging
from backend.agents.diagnosis_agent import run_diagnosis
from backend.agents.recommendation_agent import run_recommendation
from backend.agents.explanation_agent import run_explanation

logger = logging.getLogger(__name__)

class AnomalyMemory:
    """Simple in-memory store for the last 5 incident summaries."""
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

    def get_context(self) -> str:
        if not self.history:
            return "No previous anomalies recorded."
        return "\n".join([f"- {h['timestamp']}: {h['issue']} ({h['severity']})" for h in self.history])

# Initialize memory
memory = AnomalyMemory()

def trigger_agent_pipeline(anomaly_event: dict) -> dict:
    """
    Event Bus — orchestrates the 3-agent pipeline with memory context.
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    context = memory.get_context()
    
    logger.info("🩺 Running Specialized Diagnosis Agent...")
    diagnosis = run_diagnosis(anomaly_event, context)

    logger.info("🔧 Running Specialized Recommendation Agent...")
    recommendation = run_recommendation(anomaly_event, diagnosis, context)

    logger.info("📢 Running Specialized Explanation Agent...")
    explanation = run_explanation(anomaly_event, diagnosis, recommendation, context)

    result = {
        **anomaly_event,
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
