"""Cached access to the processed datasets. Each worker reads each file once."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from betting_dashboard.analytics.betting import grade_predictions
from betting_dashboard.config import settings
from betting_dashboard.data.schema import (
    ARCHIVE_COLUMNS,
    GAME_COLUMNS,
    PREDICTION_COLUMNS,
    validate,
)


def _read(name: str, columns: dict[str, str]) -> pd.DataFrame:
    return validate(pd.read_parquet(settings.data_dir / f"{name}.parquet"), columns, name)


@lru_cache(maxsize=1)
def games() -> pd.DataFrame:
    return _read("games", GAME_COLUMNS)


@lru_cache(maxsize=1)
def predictions() -> pd.DataFrame:
    """The prediction archive with every pick graded."""
    return grade_predictions(_read("predictions", ARCHIVE_COLUMNS))


@lru_cache(maxsize=1)
def upcoming() -> pd.DataFrame:
    return _read("upcoming", PREDICTION_COLUMNS)
