"""Game data: the whole historical table, loaded on demand from the server."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update

from betting_dashboard.analytics import games as g
from betting_dashboard.analytics.grid_query import TEAM_COLUMN, apply_filter_model, rows_for_request
from betting_dashboard.components.grid import (
    FMT_ODDS,
    FMT_PCT,
    col,
    data_grid,
    date_col,
    num_col,
    text_col,
)
from betting_dashboard.components.layout import card, dropdown, field, icon, page_header
from betting_dashboard.config import settings
from betting_dashboard.data import store

PATH = "/games"
NAME = "Game data"
TITLE = "Game data"
DESCRIPTION = "35,000+ basketball games with scores, lines and odds, 2010–2021."

COLUMNS = [
    date_col(pinned="left"),
    text_col("season", "Season", minWidth=100),
    text_col("league", "Competition", minWidth=160),
    text_col("home_team", "Home", minWidth=150),
    text_col("away_team", "Away", minWidth=150),
    num_col("home_score", "Home pts"),
    num_col("away_score", "Away pts"),
    num_col("total_points", "Total"),
    num_col("line", "Line"),
    text_col("total_result", "O/U", minWidth=90),
    num_col("odd_home", "Home odds", FMT_ODDS),
    num_col("odd_away", "Away odds", FMT_ODDS),
    num_col("odd_over", "Over odds", FMT_ODDS),
    num_col("odd_under", "Under odds", FMT_ODDS),
    num_col("home_implied_prob", "Home impl. prob.", FMT_PCT),
    # Hidden column so the Team box can filter home OR away through the grid's filter model.
    col(TEAM_COLUMN, "Team", hide=True, filter="agTextColumnFilter"),
]
EXPORT_COLUMNS = [c["field"] for c in COLUMNS if c["field"] != TEAM_COLUMN]


def layout(**_query: str) -> html.Div:
    games = store.games()
    return html.Div(
        [
            page_header(
                "Game data",
                "Every game in the dataset. Use the quick filters or any column filter; rows "
                "load as you scroll.",
            ),
            card(
                dbc.Row(
                    [
                        field(
                            "Season",
                            dropdown("gm-season", g.seasons(games), placeholder="All seasons"),
                        ),
                        field(
                            "Competition",
                            dropdown("gm-league", g.leagues(games), placeholder="All competitions"),
                        ),
                        field(
                            "Team (home or away)",
                            dropdown("gm-team", g.teams(games), placeholder="Any team"),
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(id="gm-count", className="muted small"),
                                    dbc.Button(
                                        [icon("bi-download", className="me-2"), "Export CSV"],
                                        id="gm-export",
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                    )
                                    if settings.allow_csv_export
                                    else None,
                                ],
                                className="d-flex flex-column align-items-lg-end gap-2 h-100 "
                                "justify-content-end",
                            ),
                            xs=12,
                            lg=3,
                        ),
                    ],
                    className="g-3",
                ),
                className="mb-4",
            ),
            card(data_grid("gm-grid", COLUMNS, infinite=True, height=640)),
            dcc.Download(id="gm-download"),
        ]
    )


@callback(
    Output("gm-grid", "filterModel"),
    Input("gm-season", "value"),
    Input("gm-league", "value"),
    Input("gm-team", "value"),
    State("gm-grid", "filterModel"),
)
def quick_filters(season, league, team, current):
    model = {k: v for k, v in (current or {}).items() if k not in {"season", "league", TEAM_COLUMN}}
    for column, value in (("season", season), ("league", league), (TEAM_COLUMN, team)):
        if value:
            model[column] = {"filterType": "text", "type": "equals", "filter": value}
    return model


@callback(
    Output("gm-grid", "getRowsResponse"),
    Output("gm-count", "children"),
    Input("gm-grid", "getRowsRequest"),
)
def serve_rows(request):
    if not request:
        return no_update, no_update
    response = rows_for_request(store.games()[EXPORT_COLUMNS], request)
    return response, f"{response['rowCount']:,} games"


if settings.allow_csv_export:

    @callback(
        Output("gm-download", "data"),
        Input("gm-export", "n_clicks"),
        State("gm-grid", "filterModel"),
        prevent_initial_call=True,
    )
    def export_csv(_n, filter_model):
        df = apply_filter_model(store.games()[EXPORT_COLUMNS], filter_model)
        return dcc.send_data_frame(df.to_csv, "basketball_games.csv", index=False)
