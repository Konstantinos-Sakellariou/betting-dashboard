"""Number formatting for the UI. Every helper renders NaN as an em dash."""

from __future__ import annotations

import math

DASH = "—"


def _missing(value: float | None) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def pct(value: float | None, digits: int = 1) -> str:
    return DASH if _missing(value) else f"{value * 100:.{digits}f}%"


def signed_pct(value: float | None, digits: int = 1) -> str:
    return DASH if _missing(value) else f"{value * 100:+.{digits}f}%"


def signed_points(value: float | None) -> str:
    """A difference between two rates, in percentage points."""
    return DASH if _missing(value) else f"{value * 100:+.1f} pts"


def units(value: float | None) -> str:
    return DASH if _missing(value) else f"{value:+.1f}u"


def number(value: float | None, digits: int = 0) -> str:
    return DASH if _missing(value) else f"{value:,.{digits}f}"


def tone(value: float | None) -> str:
    """'win' | 'loss' | 'neutral' for colouring a signed figure."""
    if _missing(value) or abs(value) < 1e-9:
        return "neutral"
    return "win" if value > 0 else "loss"
