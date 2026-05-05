import requests
import logging

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3"

logger = logging.getLogger(__name__)


def query_gemma(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send a prompt to a locally-running Ollama model and return the response text.
    Falls back gracefully if Ollama is not running.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        logger.warning("Ollama not reachable — returning mock response.")
        return _mock_response(prompt)
    except Exception as exc:
        logger.error("Gemma query failed: %s", exc)
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """Return a realistic mock response when Ollama is offline (demo fallback)."""
    if "diagnosis" in prompt.lower() or "what is happening" in prompt.lower():
        return (
            "A sudden latency spike combined with elevated packet loss indicates "
            "network congestion or a potential DDoS attack targeting the upstream router. "
            "The anomaly pattern is consistent with TCP retransmission storms."
        )
    if "recommend" in prompt.lower() or "action" in prompt.lower():
        return (
            "1. Throttle non-critical traffic using QoS rules.\n"
            "2. Check upstream BGP routes for unexpected route changes.\n"
            "3. Enable rate-limiting on the edge firewall.\n"
            "4. Alert the NOC team for manual inspection."
        )
    return (
        "⚠️ Anomaly Detected: Network metrics have deviated significantly from baseline. "
        "Latency is 22× above normal and packet loss exceeds 15%. "
        "Immediate investigation is recommended."
    )
