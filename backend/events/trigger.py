import logging
from backend.agents.diagnosis_agent import run_diagnosis
from backend.agents.recommendation_agent import run_recommendation
from backend.agents.explanation_agent import run_explanation

logger = logging.getLogger(__name__)


def trigger_agent_pipeline(anomaly_event: dict) -> dict:
    """
    Event Bus — receives an anomaly event and orchestrates the 3-agent pipeline.

    Pipeline:
        1. Diagnosis Agent   → what is happening
        2. Recommendation Agent → what to do
        3. Explanation Agent → human-readable summary

    Returns a fully populated incident response dict.
    """
    if not anomaly_event.get("anomaly"):
        return {**anomaly_event, "agents": None}

    logger.info(
        "🔴 Anomaly triggered | severity=%s | metric=%s | ts=%s",
        anomaly_event["severity"],
        anomaly_event["primary_metric"],
        anomaly_event["timestamp"],
    )

    logger.info("🩺 Running Diagnosis Agent...")
    diagnosis = run_diagnosis(anomaly_event)

    logger.info("🔧 Running Recommendation Agent...")
    recommendation = run_recommendation(anomaly_event, diagnosis)

    logger.info("📢 Running Explanation Agent...")
    explanation = run_explanation(anomaly_event, diagnosis, recommendation)

    return {
        **anomaly_event,
        "agents": {
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "explanation": explanation,
        },
    }
