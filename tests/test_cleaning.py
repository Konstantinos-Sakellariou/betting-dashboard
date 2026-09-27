import pandas as pd
import pytest

from betting_dashboard.data.cleaning import (
    clean_archive,
    repair_swapped_dates,
    season_of,
    total_result,
)
from betting_dashboard.data.schema import GAME_COLUMNS, validate


def test_repair_swapped_dates_swaps_only_ambiguous_days():
    # 6 Oct 2010 had been mis-parsed as 10 Jun 2010; 30 Nov 2017 was unambiguous.
    stored = pd.Series(["2010-06-10", "2017-11-30", "2011-12-01"])
    repaired = repair_swapped_dates(stored)
    assert repaired.dt.strftime("%Y-%m-%d").tolist() == ["2010-10-06", "2017-11-30", "2011-01-12"]


def test_season_starts_in_august():
    dates = pd.to_datetime(pd.Series(["2019-07-31", "2019-08-01", "2020-03-15", "2009-12-01"]))
    assert season_of(dates).tolist() == ["2018-19", "2019-20", "2019-20", "2009-10"]


def test_total_result_handles_push():
    total = pd.Series([160, 150, 155])
    line = pd.Series([155.5, 155.5, 155.0])
    assert total_result(total, line).tolist() == ["over", "under", "push"]


def _raw_archive(**overrides):
    row = {
        "Date": "25/09/2021",
        "Time": "16:00:00",
        "League": "ACB",
        "Home_Team": "Barcelona",
        "Away_Team": "Breogan",
        "Odd_Home_Mean": 1.07,
        "Odd_Away_Mean": 9.32,
        "Pred_Score_Home": 84.0,
        "Pred_Score_Away": 67.0,
        "Predicted_Result": "Assos",
        "Predicted_Points_Sum": 151.0,
        "Line": 155.0,
        "Predicted_Line": "Under",
        "Difference": 4.0,
        "Actual_Score_Home": 78.0,
        "Actual_Score_Away": 69.0,
    }
    row.update(overrides)
    return row


def test_clean_archive_maps_labels_and_dedupes():
    raw = pd.DataFrame(
        [
            _raw_archive(),
            _raw_archive(),  # exact duplicate
            _raw_archive(
                Home_Team="Tenerife", Predicted_Result="Diplo", Predicted_Points_Sum=155.0
            ),
        ]
    )
    df = clean_archive(raw)
    assert len(df) == 2
    barca = df[df.home_team == "Barcelona"].iloc[0]
    assert barca.league == "Liga ACB"
    assert barca.ml_pick == "home"
    assert barca.total_pick == "under"
    assert barca.edge == 4.0
    assert barca.date == pd.Timestamp("2021-09-25")
    tenerife = df[df.home_team == "Tenerife"].iloc[0]
    assert tenerife.ml_pick == "away"
    assert pd.isna(tenerife.total_pick)  # predicted total equals the line: no pick


def test_validate_rejects_missing_columns():
    with pytest.raises(ValueError, match="missing"):
        validate(pd.DataFrame({"date": []}), GAME_COLUMNS, "games")
