"""Column contracts and display metadata for the processed datasets.

Anything that writes `data/processed/*.parquet` (today: `scripts/build_data.py`, later: the
live pipeline) must produce exactly these columns. `validate()` enforces it.
"""

from __future__ import annotations

import pandas as pd

# Raw league codes -> display names. Order is used for legends and dropdowns.
LEAGUES: dict[str, str] = {
    "NBA": "NBA",
    "Euroleague": "EuroLeague",
    "Eurocup": "EuroCup",
    "Champions-League": "Basketball Champions League",
    "ACB": "Liga ACB",
    "Lega-A": "Lega Basket Serie A",
    "LNB": "LNB Pro A",
    "BBL": "Basketball Bundesliga",
    "Basket-League": "Greek Basket League",
    "Super-Lig": "Turkish Super League",
    "VTB": "VTB United League",
    "ABA-League": "ABA League",
    "LKL": "LKL (Lithuania)",
    "Greek Cup": "Greek Cup",
    "Spanish Cup": "Copa del Rey",
    "Turkish Cup": "Turkish Cup",
}
LEAGUE_ORDER: list[str] = list(LEAGUES.values())

GAME_COLUMNS: dict[str, str] = {
    "date": "datetime",
    "tip_off": "str",
    "season": "str",
    "league": "str",
    "home_team": "str",
    "away_team": "str",
    "home_score": "int",
    "away_score": "int",
    "total_points": "int",
    "margin": "int",
    "winner": "str",  # home | away
    "line": "float",
    "total_result": "str",  # over | under | push
    "odd_over": "float",
    "odd_under": "float",
    "odd_home": "float",
    "odd_away": "float",
    "odd_home_open": "float",
    "odd_home_close": "float",
    "odd_away_open": "float",
    "odd_away_close": "float",
    "home_implied_prob": "float",
    "away_implied_prob": "float",
    "home_avg_points": "float",
    "away_avg_points": "float",
    "home_avg_points_at_home": "float",
    "away_avg_points_away": "float",
}

PREDICTION_COLUMNS: dict[str, str] = {
    "date": "datetime",
    "tip_off": "str",
    "league": "str",
    "home_team": "str",
    "away_team": "str",
    "odd_home": "float",
    "odd_away": "float",
    "pred_home_score": "float",
    "pred_away_score": "float",
    "pred_total": "float",
    "line": "float",
    "edge": "float",
    "ml_pick": "str",  # home | away
    "total_pick": "str",  # over | under | <NA> when prediction == line
}

ARCHIVE_COLUMNS: dict[str, str] = {
    **PREDICTION_COLUMNS,
    "home_score": "int",
    "away_score": "int",
}

# Human labels for numeric features the explorer lets people plot.
FEATURE_LABELS: dict[str, str] = {
    "total_points": "Total points",
    "home_score": "Home points",
    "away_score": "Away points",
    "margin": "Home margin",
    "line": "Total points line",
    "odd_home": "Home odds (market mean)",
    "odd_away": "Away odds (market mean)",
    "odd_over": "Over odds",
    "odd_under": "Under odds",
    "home_implied_prob": "Home implied win prob.",
    "away_implied_prob": "Away implied win prob.",
    "home_avg_points": "Home team avg points",
    "away_avg_points": "Away team avg points",
    "home_avg_points_at_home": "Home team avg points at home",
    "away_avg_points_away": "Away team avg points away",
}


def validate(df: pd.DataFrame, columns: dict[str, str], name: str) -> pd.DataFrame:
    """Fail loudly if `df` does not match the contract; return it with columns in order."""
    missing = set(columns) - set(df.columns)
    extra = set(df.columns) - set(columns)
    if missing or extra:
        raise ValueError(f"{name}: missing={sorted(missing)} unexpected={sorted(extra)}")
    for col, kind in columns.items():
        if not _KIND_CHECKS[kind](df[col]):
            raise TypeError(f"{name}.{col}: expected {kind}, got {df[col].dtype}")
    return df[list(columns)]


_KIND_CHECKS = {
    "datetime": pd.api.types.is_datetime64_dtype,
    "str": pd.api.types.is_string_dtype,
    "int": pd.api.types.is_integer_dtype,
    "float": pd.api.types.is_float_dtype,
}
