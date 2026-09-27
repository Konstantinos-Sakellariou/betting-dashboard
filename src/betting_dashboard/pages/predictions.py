"""Predictions: the latest published slate and the full graded archive."""

from __future__ import annotations

from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, html

from betting_dashboard.analytics.betting import RECOMMENDED_EDGE
from betting_dashboard.analytics.grid_query import to_records
from betting_dashboard.components.grid import (
    FMT_1DP,
    FMT_ODDS,
    FMT_UNITS,
    SIGN_CLASSES,
    data_grid,
    date_col,
    num_col,
    result_col,
    text_col,
)
from betting_dashboard.components.layout import card, icon, page_header
from betting_dashboard.config import settings
from betting_dashboard.data import store

PATH = "/predictions"
NAME = "Predictions"
TITLE = "Predictions"
DESCRIPTION = "Latest published basketball predictions and every graded pick since 2021."

RECOMMENDED_FILTER = {
    "edge": {"filterType": "number", "type": "greaterThan", "filter": RECOMMENDED_EDGE}
}
PICK_LABELS = {"over": "Over", "under": "Under", "home": "Home", "away": "Away"}


def is_stale(slate: pd.DataFrame, today: date | None = None) -> bool:
    if slate.empty:
        return True
    today = today or date.today()
    return (today - slate["date"].max().date()).days > settings.stale_after_days


def layout(**_query: str) -> html.Div:
    slate = store.upcoming()
    preds = store.predictions()

    banner = None
    if is_stale(slate):
        span = (
            f"{slate['date'].min():%d %b %Y}"
            if slate["date"].min() == slate["date"].max()
            else f"{slate['date'].min():%d} – {slate['date'].max():%d %b %Y}"
        )
        banner = dbc.Alert(
            [
                icon("bi-pause-circle-fill", className="me-2"),
                html.Strong("Live predictions are paused. "),
                f"Below is the last slate the model published ({span}). The track record "
                "further down is complete and graded.",
            ],
            color="warning",
            className="stale-banner",
        )

    return html.Div(
        [
            page_header(
                "Predictions",
                "Predicted scores for each game, the totals pick against the bookmaker line, "
                "and the moneyline pick.",
            ),
            banner,
            html.H2("Latest slate", className="section-title"),
            html.P(
                [
                    "Recommended picks (★) have a totals edge above ",
                    html.Strong(f"{RECOMMENDED_EDGE:g} points"),
                    " and are listed first.",
                ],
                className="section-sub",
            ),
            dbc.Row(
                [
                    dbc.Col(_slate_card(row), xs=12, md=6, xl=4)
                    for row in _slate_order(slate).itertuples()
                ],
                className="g-3 mb-5",
            ),
            html.H2("Track record", className="section-title"),
            html.P(
                [
                    "Every published pick, graded against the final score. It opens on the "
                    "recommended picks (edge above ",
                    html.Strong(f"{RECOMMENDED_EDGE:g} points"),
                    "); switch the toggle off to see all of them. Filter any column, or sort by "
                    "clicking its header.",
                ],
                className="section-sub",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Switch(
                            id="pred-recommended",
                            label=f"Only recommended picks (edge > {RECOMMENDED_EDGE:g})",
                            value=True,
                        ),
                        xs="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            [icon("bi-download", className="me-2"), "Export CSV"],
                            id="pred-export",
                            color="secondary",
                            outline=True,
                            size="sm",
                        )
                        if settings.allow_csv_export
                        else None,
                        xs="auto",
                        className="ms-auto",
                    ),
                ],
                className="align-items-center mb-2 g-2",
            ),
            card(
                data_grid(
                    "pred-archive",
                    GRID_COLUMNS,
                    to_records(_archive_rows(preds)),
                    height=620,
                    filterModel=RECOMMENDED_FILTER,
                    csvExportParams={"fileName": "prediction_archive.csv"},
                )
            ),
        ]
    )


def _slate_order(slate: pd.DataFrame) -> pd.DataFrame:
    """Recommended picks first, then by kick-off."""
    return slate.assign(_rec=slate["edge"] > RECOMMENDED_EDGE).sort_values(
        ["_rec", "date", "tip_off"], ascending=[False, True, True], kind="stable"
    )


def _slate_card(row) -> dbc.Card:
    strong = row.edge > RECOMMENDED_EDGE
    total_pick = PICK_LABELS.get(row.total_pick) if isinstance(row.total_pick, str) else None
    ml_team = row.home_team if row.ml_pick == "home" else row.away_team
    ml_odds = row.odd_home if row.ml_pick == "home" else row.odd_away
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span(row.league, className="chip"),
                        html.Span(f"{row.date:%a %d %b} · {row.tip_off}", className="muted small"),
                    ],
                    className="d-flex justify-content-between align-items-center mb-2",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Span(row.home_team), html.Span(f"{row.pred_home_score:.0f}")],
                            className="matchup-row",
                        ),
                        html.Div(
                            [html.Span(row.away_team), html.Span(f"{row.pred_away_score:.0f}")],
                            className="matchup-row",
                        ),
                    ],
                    className="matchup",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Total", className="pick-label"),
                                html.Div(
                                    f"{total_pick} {row.line:g}" if total_pick else "No pick",
                                    className="pick-value",
                                ),
                                html.Div(
                                    f"Predicted {row.pred_total:.0f} · edge {row.edge:g}",
                                    className="pick-sub",
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.Div("Winner", className="pick-label"),
                                html.Div(ml_team, className="pick-value"),
                                html.Div(f"@ {ml_odds:.2f}", className="pick-sub"),
                            ],
                            className="text-end",
                        ),
                    ],
                    className="picks",
                ),
                html.Span(
                    [icon("bi-star-fill", className="me-1"), "Recommended"],
                    className="badge-strong",
                )
                if strong
                else None,
            ]
        ),
        className="slate-card" + (" slate-card-strong" if strong else ""),
    )


def _archive_rows(preds: pd.DataFrame) -> pd.DataFrame:
    rows = preds.assign(
        predicted=lambda d: (
            d["pred_home_score"].map("{:.0f}".format)
            + "–"
            + d["pred_away_score"].map("{:.0f}".format)
        ),
        final=lambda d: d["home_score"].astype(str) + "–" + d["away_score"].astype(str),
        total_pick=lambda d: d["total_pick"].map(PICK_LABELS),
        ml_pick=lambda d: d["ml_pick"].map(PICK_LABELS),
    )
    return rows[[c["field"] for c in GRID_COLUMNS]].sort_values("date", ascending=False)


GRID_COLUMNS = [
    date_col(pinned="left", sort="desc"),
    text_col("league", "League", minWidth=150),
    text_col("home_team", "Home", minWidth=140),
    text_col("away_team", "Away", minWidth=140),
    text_col("predicted", "Predicted", minWidth=100, filter=False),
    text_col("final", "Final", minWidth=90, filter=False),
    num_col("line", "Line", FMT_1DP),
    num_col("edge", "Edge", FMT_1DP),
    text_col("total_pick", "Total pick", minWidth=110),
    result_col("total_result", "Total result"),
    num_col("total_units", "Total units", FMT_UNITS, cellClassRules=SIGN_CLASSES),
    text_col("ml_pick", "ML pick", minWidth=100),
    num_col("ml_odds", "ML odds", FMT_ODDS),
    result_col("ml_result", "ML result"),
    num_col("ml_units", "ML units", FMT_UNITS, cellClassRules=SIGN_CLASSES),
]


@callback(
    Output("pred-archive", "filterModel"),
    Input("pred-recommended", "value"),
    prevent_initial_call=True,
)
def toggle_recommended(only_recommended: bool):
    return RECOMMENDED_FILTER if only_recommended else {}


if settings.allow_csv_export:

    @callback(
        Output("pred-archive", "exportDataAsCsv"),
        Input("pred-export", "n_clicks"),
        prevent_initial_call=True,
    )
    def export_archive(_n: int) -> bool:
        return True
