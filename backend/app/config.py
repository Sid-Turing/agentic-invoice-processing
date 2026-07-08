"""Runtime configuration sourced from the environment.

All secrets (model keys, DATABASE_URL) come from the environment / a local .env;
nothing is committed. Business tolerances carry over from the original app and are
overridable via env so behaviour is tunable without code changes.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw else default


@dataclass(frozen=True)
class Settings:
    # Providers
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    openai_model_id: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL_ID", "gpt-5.5-2026-04-23"))
    gemini_model_id: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL_ID", "gemini-3.5-flash"))

    # Database (swappable via env)
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql+psycopg2://invoice:invoice@localhost:5432/invoices"
        )
    )

    # Data / uploads
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", str(_REPO_ROOT / "data"))))
    max_upload_mb: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_MB", "10")))

    # Business config
    tax_rate: float = field(default_factory=lambda: _float("TAX_RATE", 0.09125))
    supported_currencies: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            c.strip().upper() for c in os.getenv("SUPPORTED_CURRENCIES", "USD").split(",") if c.strip()
        )
    )

    # Tolerances (carried from the original app)
    total_tolerance: float = field(default_factory=lambda: _float("TOTAL_TOLERANCE", 0.02))
    line_tolerance: float = field(default_factory=lambda: _float("LINE_TOLERANCE", 0.02))
    po_qty_tolerance: float = field(default_factory=lambda: _float("PO_QTY_TOLERANCE", 0.10))
    po_unit_price_tolerance: float = field(default_factory=lambda: _float("PO_UNIT_PRICE_TOLERANCE", 0.05))
    po_total_price_tolerance: float = field(default_factory=lambda: _float("PO_TOTAL_PRICE_TOLERANCE", 0.05))
    vendor_match_threshold: float = field(default_factory=lambda: _float("VENDOR_MATCH_THRESHOLD", 0.70))
    tax_discrepancy_tolerance: float = field(default_factory=lambda: _float("TAX_DISCREPANCY_TOLERANCE", 0.25))

    # Reporting (feature 002)
    high_value_threshold: float = field(default_factory=lambda: _float("HIGH_VALUE_THRESHOLD", 3000.0))
    default_page_size: int = field(default_factory=lambda: int(os.getenv("DEFAULT_PAGE_SIZE", "25")))
    max_page_size: int = field(default_factory=lambda: int(os.getenv("MAX_PAGE_SIZE", "100")))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
