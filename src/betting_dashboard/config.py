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
    author_name: str
    repo_url: str
    github_url: str | None
    linkedin_url: str | None
    portfolio_url: str | None
    contact_email: str | None
    allow_csv_export: bool
    stale_after_days: int
    debug: bool


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def _env_optional(name: str, default: str) -> str | None:
    """`default` when unset; an explicitly empty value hides the item."""
    value = os.getenv(name, default).strip()
    return value or None


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Courtside Analytics"),
        data_dir=Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data" / "processed")),
        author_name=os.getenv("AUTHOR_NAME", "Konstantinos Sakellariou"),
        repo_url=os.getenv(
            "REPO_URL", "https://github.com/Konstantinos-Sakellariou/betting-dashboard"
        ),
        github_url=_env_optional("GITHUB_URL", "https://github.com/Konstantinos-Sakellariou"),
        linkedin_url=_env_optional(
            "LINKEDIN_URL", "https://www.linkedin.com/in/konstantinos-sakellariou/"
        ),
        portfolio_url=_env_optional("PORTFOLIO_URL", "https://konstantinos-sakellariou.github.io/"),
        contact_email=_env_optional("CONTACT_EMAIL", "konstantinossakellariou@gmail.com"),
        allow_csv_export=_env_bool("ALLOW_CSV_EXPORT", True),
        stale_after_days=int(os.getenv("STALE_AFTER_DAYS", "3")),
        debug=_env_bool("DEBUG", False),
    )


settings = load_settings()
