import math

import pandas as pd
import pytest

from betting_dashboard.analytics.betting import (
    RECOMMENDED_EDGE,
    TOTALS_ASSUMED_ODDS,
    cumulative_units,
    edge_curve,
    grade_predictions,
    record,
    record_by,
    with_min_edge,
)


def _archive(rows):
    defaults = {
        "date": pd.Timestamp("2022-01-01"),
        "league": "EuroLeague",
        "odd_home": 1.5,
        "odd_away": 2.6,
        "line": 160.5,
        "edge": 3.0,
        "ml_pick": "home",
        "total_pick": "over",
        "home_score": 85,
        "away_score": 80,
    }
    df = pd.DataFrame([{**defaults, **r} for r in rows])
    df["total_pick"] = df["total_pick"].astype("str")
    return grade_predictions(df)


def test_moneyline_win_pays_odds_minus_one():
    df = _archive([{"ml_pick": "home", "odd_home": 1.5}])
    assert df.ml_result.iloc[0] == "win"
    assert df.ml_units.iloc[0] == pytest.approx(0.5)


def test_moneyline_loss_costs_one_unit():
    df = _archive([{"ml_pick": "away"}])
    assert df.ml_result.iloc[0] == "loss"
    assert df.ml_units.iloc[0] == -1


def test_totals_grading_win_loss_push_and_no_pick():
    df = _archive(
        [
            {"total_pick": "over", "line": 160.5},  # 165 > 160.5 -> win
            {"total_pick": "under", "line": 160.5},  # loss
            {"total_pick": "under", "line": 165.0},  # exactly on the line -> push
            {"total_pick": None},  # no pick
        ]
    )
    assert df.total_result.tolist()[:3] == ["win", "loss", "push"]
    assert pd.isna(df.total_result.iloc[3])
    assert df.total_units.tolist()[:3] == pytest.approx([TOTALS_ASSUMED_ODDS - 1, -1, 0])
    assert math.isnan(df.total_units.iloc[3])


def test_record_excludes_pushes_from_hit_rate_and_roi():
    df = _archive(
        [
            {"total_pick": "over"},
            {"total_pick": "under"},
            {"total_pick": "under", "line": 165.0},
            {"total_pick": None},
        ]
    )
    rec = record(df, "total")
    assert (rec.picks, rec.wins, rec.losses, rec.pushes) == (3, 1, 1, 1)
    assert rec.hit_rate == 0.5
    assert rec.units == pytest.approx(TOTALS_ASSUMED_ODDS - 2)
    assert rec.roi == pytest.approx((TOTALS_ASSUMED_ODDS - 2) / 2)
    assert rec.break_even == pytest.approx(1 / TOTALS_ASSUMED_ODDS)


def test_record_of_empty_frame_is_nan_not_error():
    rec = record(_archive([{"total_pick": None}]), "total")
    assert rec.picks == 0
    assert math.isnan(rec.hit_rate)
    assert math.isnan(rec.roi)


def test_record_by_groups():
    df = _archive([{"league": "A"}, {"league": "A"}, {"league": "B", "ml_pick": "away"}])
    table = record_by(df, "league", "ml")
    assert table.league.tolist() == ["A", "B"]
    assert table.picks.tolist() == [2, 1]
    assert table.wins.tolist() == [2, 0]


def test_cumulative_units_runs_by_date():
    df = _archive(
        [
            {"date": pd.Timestamp("2022-01-01")},
            {"date": pd.Timestamp("2022-01-01"), "ml_pick": "away"},
            {"date": pd.Timestamp("2022-01-02")},
        ]
    )
    daily = cumulative_units(df, "ml")
    assert daily.picks.tolist() == [2, 1]
    assert daily.cumulative_units.tolist() == pytest.approx([-0.5, 0.0])


def test_edge_curve_uses_strict_threshold():
    df = _archive([{"edge": 2.5}, {"edge": 3.0}])
    curve = edge_curve(df, [2.5])
    assert curve.picks.tolist() == [1]


def test_with_min_edge_zero_keeps_no_pick_games():
    df = _archive([{"edge": 0.0, "total_pick": None}, {"edge": 3.0}])
    assert len(with_min_edge(df, 0)) == 2
    assert len(with_min_edge(df, None)) == 2
    assert with_min_edge(df, RECOMMENDED_EDGE).edge.tolist() == [3.0]
