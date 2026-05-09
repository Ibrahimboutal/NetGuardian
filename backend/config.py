import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


def _csv_list(value: str | None, fallback: list[str]) -> list[str]:
    if not value:
        return fallback
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    api_host: str = os.getenv("NETGUARDIAN_API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("NETGUARDIAN_API_PORT", "8000"))
    frontend_origins: list[str] = None  # type: ignore[assignment]
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:9b")
    api_token: str = os.getenv("NETGUARDIAN_API_TOKEN", "change-me")
    rate_limit_requests: int = int(os.getenv("NETGUARDIAN_RATE_LIMIT_REQUESTS", "60"))
    rate_limit_window_sec: int = int(os.getenv("NETGUARDIAN_RATE_LIMIT_WINDOW_SEC", "60"))
    incident_retention_count: int = int(os.getenv("NETGUARDIAN_INCIDENT_RETENTION_COUNT", "200"))
    incident_log_max_bytes: int = int(os.getenv("NETGUARDIAN_INCIDENT_LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    model_dir: Path = Path(os.getenv("NETGUARDIAN_MODEL_DIR", str(DATA_DIR / "models")))
    alerts_webhook_url: str | None = os.getenv("NETGUARDIAN_ALERTS_WEBHOOK_URL")
    allow_auto_isolate: bool = os.getenv("NETGUARDIAN_ALLOW_AUTO_ISOLATE", "false").lower() == "true"
    environment: str = os.getenv("NETGUARDIAN_ENV", "dev")

    def __post_init__(self):
        defaults = ["http://localhost:5173", "http://localhost:3000"]
        object.__setattr__(
            self,
            "frontend_origins",
            _csv_list(os.getenv("NETGUARDIAN_CORS_ORIGINS"), defaults),
        )
        self.model_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()

