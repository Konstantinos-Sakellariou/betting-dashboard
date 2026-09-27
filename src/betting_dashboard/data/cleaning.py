"""Pure transforms from the legacy raw CSVs to the processed schemas.

See docs/DATA.md for the reasoning behind each rule.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from betting_dashboard.data.schema import (
    ARCHIVE_COLUMNS,
    GAME_COLUMNS,
    LEAGUES,
    PREDICTION_COLUMNS,
    validate,
)

SEASON_START_MONTH = 8  # a season runs from August to July


def repair_swapped_dates(dates: pd.Series) -> pd.Series:
    """Undo a month-first parse of day-first dates.

    The legacy European data was written as dd/mm/yyyy and later parsed month-first
    wherever that was possible (day <= 12), so 6 Oct 2010 became 10 Jun 2010. Dates whose
    day is > 12 could only have been parsed day-first and are already correct.
    """
    dates = pd.to_datetime(dates)
    swapped = pd.to_datetime(
        pd.DataFrame({"year": dates.dt.year, "month": dates.dt.day, "day": dates.dt.month}),
        errors="coerce",
    )
    return dates.where(dates.dt.day > 12, swapped)


def season_of(dates: pd.Series) -> pd.Series:
    """Season label such as '2019-20' for each date."""
    start = dates.dt.year - (dates.dt.month < SEASON_START_MONTH).astype(int)
    return start.astype(str) + "-" + ((start + 1) % 100).astype(str).str.zfill(2)


def total_result(total: pd.Series, line: pd.Series) -> pd.Series:
    """'over', 'under' or 'push' for each game against its totals line."""
    out = np.select([total > line, total < line], ["over", "under"], default="push")
    return pd.Series(out, index=total.index, dtype="str")


def _league_names(codes: pd.Series) -> pd.Series:
    return codes.map(LEAGUES).fillna(codes)


def _tip_off(times: pd.Series) -> pd.Series:
    return times.astype(str).str.slice(0, 5)


def clean_games(raw: pd.DataFrame) -> pd.DataFrame:
    """Legacy `nba_plus_europe.csv` -> processed games table."""
    is_nba = raw["League"].eq("NBA")
    raw_dates = pd.to_datetime(raw["Date"])
    dates = raw_dates.where(is_nba, repair_swapped_dates(raw_dates))

    df = pd.DataFrame(
        {
            "date": dates,
            "tip_off": _tip_off(raw["Time"]),
            "season": season_of(dates),
            "league": _league_names(raw["League"]),
            "home_team": raw["Home_Team"].str.strip(),
            "away_team": raw["Away_Team"].str.strip(),
            "home_score": raw["Score_home"].astype("int64"),
            "away_score": raw["Score_away"].astype("int64"),
            "line": raw["Line"].astype(float),
            "odd_over": raw["Odd_Over"],
            "odd_under": raw["Odd_Under"],
            "odd_home": raw["Odd_Home_Mean"],
            "odd_away": raw["Odd_Away_Mean"],
            "odd_home_open": raw["Odd_Home_First"],
            "odd_home_close": raw["Odd_Home_Last"],
            "odd_away_open": raw["Odd_Away_First"],
            "odd_away_close": raw["Odd_Away_Last"],
            "home_implied_prob": raw["Mean_Home_Winning_Probability"],
            "away_implied_prob": raw["Mean_Away_Winning_Probability"],
            "home_avg_points": raw["Home_Team_Total_Scoring"],
            "away_avg_points": raw["Away_Team_Total_Scoring"],
            "home_avg_points_at_home": raw["Home_Team_Home_Scoring"],
            "away_avg_points_away": raw["Away_Team_Away_Scoring"],
        }
    )
    df["total_points"] = df["home_score"] + df["away_score"]
    df["margin"] = df["home_score"] - df["away_score"]
    df["winner"] = np.where(df["margin"] > 0, "home", "away")
    df["total_result"] = total_result(df["total_points"], df["line"])
    df = df.sort_values(["date", "tip_off", "league", "home_team"], kind="stable")
    return validate(df.reset_index(drop=True), GAME_COLUMNS, "games")


def _clean_prediction_frame(raw: pd.DataFrame, *, date_format: str | None) -> pd.DataFrame:
    pred_total = raw["Predicted_Points_Sum"].astype(float)
    line = raw["Line"].astype(float)
    total_pick = pd.Series(
        np.select([pred_total > line, pred_total < line], ["over", "under"], default=""),
        index=raw.index,
    ).replace("", pd.NA)
    return pd.DataFrame(
        {
            "date": pd.to_datetime(raw["Date"], format=date_format),
            "tip_off": _tip_off(raw["Time"]),
            "league": _league_names(raw["League"]),
            "home_team": raw["Home_Team"].str.strip(),
            "away_team": raw["Away_Team"].str.strip(),
            "odd_home": raw["Odd_Home_Mean"].astype(float),
            "odd_away": raw["Odd_Away_Mean"].astype(float),
            "pred_home_score": raw["Pred_Score_Home"].astype(float),
            "pred_away_score": raw["Pred_Score_Away"].astype(float),
            "pred_total": pred_total,
            "line": line,
            "edge": (pred_total - line).abs(),
            # 'Assos'/'Diplo' is Greek betting slang for "1"/"2" (home/away win).
            "ml_pick": raw["Predicted_Result"].map({"Assos": "home", "Diplo": "away"}),
            "total_pick": total_pick.astype("str"),
        }
    )


def clean_archive(raw: pd.DataFrame) -> pd.DataFrame:
    """Legacy `all_archive.csv` -> processed prediction archive (ungraded)."""
    df = _clean_prediction_frame(raw, date_format="%d/%m/%Y")
    df["home_score"] = raw["Actual_Score_Home"].astype("int64")
    df["away_score"] = raw["Actual_Score_Away"].astype("int64")
    df = df.drop_duplicates().sort_values(["date", "tip_off", "home_team"], kind="stable")
    return validate(df.reset_index(drop=True), ARCHIVE_COLUMNS, "predictions")


def clean_upcoming(raw: pd.DataFrame) -> pd.DataFrame:
    """Legacy `next_daysNN.csv` -> processed upcoming slate."""
    df = _clean_prediction_frame(raw, date_format="%Y-%m-%d")
    df = df.sort_values(["date", "tip_off", "home_team"], kind="stable")
    return validate(df.reset_index(drop=True), PREDICTION_COLUMNS, "upcoming")
