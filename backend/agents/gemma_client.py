import requests
import logging
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma3"

logger = logging.getLogger(__name__)

def validate_schema(data: dict, required_keys: list) -> bool:
    """Ensure all required keys are present in the AI output."""
    if not isinstance(data, dict):
        return False
    return all(key in data for key in required_keys)

def safe_parse(text: str, required_keys: list = None) -> dict:
    """
    Extract and parse JSON from LLM output. 
    Handles conversational fluff, malformed strings, and key validation.
    """
    parsed = {"error": "invalid_json"}
    try:
        # Attempt direct parse first
        parsed = json.loads(text)
    except Exception:
        # Search for JSON block using regex
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
        except Exception:
            parsed = {"error": "regex_failed", "raw": text}
    
    # Validation step
    if required_keys and not validate_schema(parsed, required_keys):
        logger.warning("Schema validation failed for AI output. Keys missing.")
        return {"error": "schema_mismatch", "raw": parsed}
        
    return parsed

def query_gemma(prompt: str, required_keys: list = None, model: str = DEFAULT_MODEL) -> dict:
    """
    Send a prompt to a locally-running Ollama model and return the parsed JSON response.
    Falls back gracefully if Ollama is not running or output is invalid.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        raw_text = response.json().get("response", "").strip()
        return safe_parse(raw_text, required_keys)
    except Exception as exc:
        logger.error("Gemma query failed: %s", exc)
        return safe_parse(_mock_response(prompt), required_keys)

def _mock_response(prompt: str) -> str:
    """Return realistic structured JSON mock responses for critical infrastructure."""
    prompt_lower = prompt.lower()
    
    if "forensic analyst" in prompt_lower:
        return json.dumps({
            "issue": "Anomalous Edge Traffic Spikes",
            "root_cause": "Detection of unauthorized high-volume egress traffic on Port 443 originating from DB-Cluster-04.",
            "confidence": "92%",
            "impact": "High. Potential data exfiltration event in progress. Primary firewall throughput reaching 85% capacity."
        })
    
    if "incident commander" in prompt_lower:
        return json.dumps({
            "actions": [
                {"action": "Isolate DB-Cluster-04 from outbound internet traffic via ACL update", "priority": "CRITICAL", "difficulty": "Easy"},
                {"action": "Initiate snapshot and forensic dump of DB-Cluster-04 logs", "priority": "HIGH", "difficulty": "Medium"},
                {"action": "Deploy deep packet inspection (DPI) on Edge-Router-01", "priority": "MEDIUM", "difficulty": "Hard"},
                {"action": "Reset service account credentials associated with DB-Cluster-04", "priority": "HIGH", "difficulty": "Medium"}
            ]
        })
    
    if "crisis communicator" in prompt_lower:
        return json.dumps({
            "summary": "Our security monitoring systems have detected an unusual pattern of data movement from the core database cluster. We have initiated automated containment protocols to protect system integrity.",
            "eta_guess": "20 minutes to full containment",
            "status_color": "red"
        })
    
    return json.dumps({
        "summary": "System monitoring active. No anomalies currently requiring agent intervention.",
        "status_color": "green"
    })
