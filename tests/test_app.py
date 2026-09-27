"""Smoke tests: the app boots, every page renders, and the main callbacks return output."""

import json

import plotly.graph_objects as go
import pytest
from plotly.utils import PlotlyJSONEncoder

from betting_dashboard.app import app, server
from betting_dashboard.pages import PAGES, explorer, games, overview, predictions, teams


@pytest.fixture(scope="module")
def client():
    return server.test_client()


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.PATH)
def test_every_page_layout_serialises(page):
    json.dumps(page.layout(), cls=PlotlyJSONEncoder)


def test_index_is_small_and_has_no_third_party_assets(client):
    html = client.get("/").get_data(as_text=True)
    assert len(html) < 50_000
    assert "googleapis" not in html
    assert "cdn.jsdelivr" not in html


def test_python_source_is_not_served_as_an_asset(client):
    assert client.get("/assets/app.py").status_code == 404


def test_overview_callback():
    compare, kpis, cumulative, leagues, footnote = overview.update_overview("total", 2.5)
    assert len(kpis) == 4
    assert len(compare) == 2  # recommended vs all picks
    assert isinstance(cumulative, go.Figure) and isinstance(leagues, go.Figure)
    assert "1.90" in footnote


def test_overview_defaults_to_recommended_strategy():
    import dash

    from betting_dashboard.analytics.betting import RECOMMENDED_EDGE

    layout = json.dumps(overview.layout(), cls=PlotlyJSONEncoder)
    assert f'"value": {RECOMMENDED_EDGE}' in layout
    assert overview.view_label(RECOMMENDED_EDGE) == "Recommended strategy"
    assert overview.view_label(0) == "All picks"
    assert len(overview.update_overview("total", 3.5)[0]) == 3  # custom view added
    assert dash.page_registry


def test_predictions_default_to_recommended():
    assert predictions.toggle_recommended(True) == predictions.RECOMMENDED_FILTER
    assert predictions.toggle_recommended(False) == {}


def test_explorer_callbacks_handle_empty_selection():
    count, _trend, _home = explorer.update_league_charts(["1999-00"], None)
    assert count.startswith("0 games")
    assert isinstance(
        explorer.update_scatter(None, ["EuroLeague"], "line", "total_points", "winner"), go.Figure
    )


def test_team_callback():
    _heading, kpis, _fig, _split, rows = teams.update_team("Olympiacos", ["2018-19"])
    assert len(kpis) == 4
    assert 0 < len(rows) < 100


def test_games_server_side_rows():
    request = {
        "startRow": 0,
        "endRow": 50,
        "sortModel": [{"colId": "total_points", "sort": "desc"}],
        "filterModel": games.quick_filters("2018-19", "EuroLeague", None, {}),
    }
    response, _count = games.serve_rows(request)
    assert 0 < response["rowCount"] < 400
    totals = [r["total_points"] for r in response["rowData"]]
    assert totals == sorted(totals, reverse=True)


def test_quick_filters_keep_column_filters():
    current = {"line": {"filterType": "number", "type": "greaterThan", "filter": 160}}
    model = games.quick_filters(None, None, "Olympiacos", current)
    assert set(model) == {"line", "team"}


def test_stale_banner_logic():
    import datetime as dt

    import pandas as pd

    slate = pd.DataFrame({"date": pd.to_datetime(["2022-05-14"])})
    assert predictions.is_stale(slate, dt.date(2026, 9, 27))
    assert not predictions.is_stale(slate, dt.date(2022, 5, 15))


def test_all_pages_registered():
    import dash

    paths = {p["path"] for p in dash.page_registry.values()}
    assert {p.PATH for p in PAGES} <= paths
    assert app.title
