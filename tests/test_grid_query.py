import pandas as pd

from betting_dashboard.analytics.grid_query import (
    apply_filter_model,
    apply_sort_model,
    rows_for_request,
    to_records,
)


def _df():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01"]),
            "home_team": ["Olympiacos", "Real Madrid", "Barcelona"],
            "away_team": ["Real Madrid", "Olympiacos", "Real Madrid"],
            "total_points": [150, 170, 160],
            "line": [155.5, float("nan"), 158.0],
        }
    )


def test_text_contains_is_case_insensitive():
    out = apply_filter_model(
        _df(), {"home_team": {"filterType": "text", "type": "contains", "filter": "real"}}
    )
    assert out.home_team.tolist() == ["Real Madrid"]


def test_number_in_range_and_compound_or():
    df = _df()
    out = apply_filter_model(
        df,
        {
            "total_points": {
                "filterType": "number",
                "type": "inRange",
                "filter": 155,
                "filterTo": 165,
            }
        },
    )
    assert out.total_points.tolist() == [160]
    out = apply_filter_model(
        df,
        {
            "total_points": {
                "filterType": "number",
                "operator": "OR",
                "conditions": [
                    {"type": "lessThan", "filter": 155},
                    {"type": "greaterThan", "filter": 165},
                ],
            }
        },
    )
    assert out.total_points.tolist() == [150, 170]


def test_date_filter():
    out = apply_filter_model(
        _df(),
        {"date": {"filterType": "date", "type": "greaterThan", "dateFrom": "2020-01-15 00:00:00"}},
    )
    assert len(out) == 2


def test_virtual_team_column_matches_either_side():
    out = apply_filter_model(
        _df(), {"team": {"filterType": "text", "type": "equals", "filter": "olympiacos"}}
    )
    assert len(out) == 2


def test_unknown_columns_and_empty_values_are_ignored():
    df = _df()
    model = {
        "nope": {"filterType": "text", "type": "contains", "filter": "x"},
        "home_team": {"filterType": "text", "type": "contains", "filter": ""},
    }
    assert len(apply_filter_model(df, model)) == 3


def test_sort_and_slice():
    df = _df()
    assert apply_sort_model(
        df, [{"colId": "total_points", "sort": "desc"}]
    ).total_points.tolist() == [
        170,
        160,
        150,
    ]
    resp = rows_for_request(
        df, {"startRow": 1, "endRow": 2, "sortModel": [{"colId": "total_points", "sort": "asc"}]}
    )
    assert resp["rowCount"] == 3
    assert [r["total_points"] for r in resp["rowData"]] == [160]


def test_records_are_json_safe():
    rec = to_records(_df())
    assert rec[0]["date"] == "2020-01-01"
    assert rec[1]["line"] is None
