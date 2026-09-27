"""Runtime settings, read from environment variables once at import."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str
    data_dir: Path
    github_url: str
    contact_email: str | None
    allow_csv_export: bool
    stale_after_days: int
    debug: bool


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Courtside Analytics"),
        data_dir=Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data" / "processed")),
        github_url=os.getenv(
            "GITHUB_URL", "https://github.com/Konstantinos-Sakellariou/betting-dashboard"
        ),
        contact_email=os.getenv("CONTACT_EMAIL") or None,
        allow_csv_export=_env_bool("ALLOW_CSV_EXPORT", True),
        stale_after_days=int(os.getenv("STALE_AFTER_DAYS", "3")),
        debug=_env_bool("DEBUG", False),
    )


settings = load_settings()
