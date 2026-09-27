"""Team profile: record, scoring by season, home/away split and recent games."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, html
from plotly.subplots import make_subplots

from betting_dashboard.analytics import games as g
from betting_dashboard.analytics.grid_query import to_records
from betting_dashboard.components import format as fmt
from betting_dashboard.components.grid import data_grid, date_col, num_col, result_col, text_col
from betting_dashboard.components.layout import (
    card,
    dropdown,
    empty_figure,
    field,
    graph,
    kpi,
    page_header,
)
from betting_dashboard.components.theme import ACCENT, INFO, MUTED
from betting_dashboard.data import store

PATH = "/teams"
NAME = "Teams"
TITLE = "Team profiles"
DESCRIPTION = "Record, scoring and over/under history for 297 basketball teams."

DEFAULT_TEAM = "Olympiacos"

RECENT_COLUMNS = [
    date_col(sort="desc"),
    text_col("league", "Competition", minWidth=150),
    text_col("venue", "Venue", minWidth=90),
    text_col("opponent", "Opponent", minWidth=150),
    text_col("score", "Score", filter=False, minWidth=90),
    result_col("result", "Result"),
    num_col("line", "Line"),
    text_col("total_result", "Over/under", minWidth=110),
]


def layout(team: str | None = None, **_query: str) -> html.Div:
    games = store.games()
    all_teams = g.teams(games)
    initial = team if team in all_teams else DEFAULT_TEAM
    return html.Div(
        [
            page_header("Team profiles", "Pick a team to see how it performed season by season."),
            card(
                dbc.Row(
                    [
                        field(
                            "Competition",
                            dropdown(
                                "tm-league",
                                g.leagues(games),
                                placeholder="All competitions",
                            ),
                            {"xs": 12, "md": 4},
                        ),
                        field(
                            "Team",
                            dropdown("tm-team", all_teams, initial, clearable=False),
                            {"xs": 12, "md": 4},
                        ),
                        field(
                            "Seasons",
                            dropdown(
                                "tm-seasons",
                                g.seasons(games),
                                multi=True,
                                placeholder="All seasons",
                            ),
                            {"xs": 12, "md": 4},
                        ),
                    ],
                    className="g-3",
                ),
                className="mb-4",
            ),
            html.Div(id="tm-heading", className="mb-3"),
            dbc.Row(id="tm-kpis", className="g-3 mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        card(
                            graph("tm-seasons-fig", height=360),
                            title="Season by season",
                            subtitle="Points scored and conceded per game (bars) and win rate "
                            "(line).",
                        ),
                        lg=8,
                    ),
                    dbc.Col(card(html.Div(id="tm-split"), title="Home vs away"), lg=4),
                ],
                className="g-4 mb-4",
            ),
            card(
                data_grid("tm-games", RECENT_COLUMNS, [], height=460),
                title="Games",
            ),
        ]
    )


@callback(
    Output("tm-team", "options"),
    Output("tm-team", "value"),
    Input("tm-league", "value"),
    State("tm-team", "value"),
)
def narrow_teams(league, current):
    options = g.teams(store.games(), league)
    return options, current if current in options else (options[0] if options else None)


@callback(
    Output("tm-heading", "children"),
    Output("tm-kpis", "children"),
    Output("tm-seasons-fig", "figure"),
    Output("tm-split", "children"),
    Output("tm-games", "rowData"),
    Input("tm-team", "value"),
    Input("tm-seasons", "value"),
)
def update_team(team, seasons):
    if not team:
        return None, [], empty_figure("Pick a team."), None, []
    games = g.filter_games(store.games(), seasons=seasons)
    played = g.team_games(games, team)
    if played.empty:
        return (
            html.H2(team, className="team-name"),
            [],
            empty_figure("No games for this team in the selected seasons."),
            None,
            [],
        )

    wins = int(played["won"].sum())
    losses = len(played) - wins
    over_rate = played["total_result"].eq("over").mean()
    heading = html.Div(
        [
            html.H2(team, className="team-name"),
            html.Span(
                f"{g.team_primary_league(games, team)} · {played['season'].nunique()} seasons · "
                f"{played['date'].min():%b %Y} – {played['date'].max():%b %Y}",
                className="muted",
            ),
        ]
    )
    kpis = [
        dbc.Col(kpi("Record", f"{wins}–{losses}", f"{len(played)} games"), xs=6, lg=3),
        dbc.Col(kpi("Win rate", fmt.pct(wins / len(played))), xs=6, lg=3),
        dbc.Col(
            kpi(
                "Points per game",
                fmt.number(played["points_for"].mean(), 1),
                f"allowed {fmt.number(played['points_against'].mean(), 1)}",
            ),
            xs=6,
            lg=3,
        ),
        dbc.Col(
            kpi("Games over the line", fmt.pct(over_rate), "share of totals landing over"),
            xs=6,
            lg=3,
        ),
    ]

    rows = played.assign(
        score=played["points_for"].astype(str) + "–" + played["points_against"].astype(str),
        result=played["won"].map({True: "win", False: "loss"}),
    )[[c["field"] for c in RECENT_COLUMNS]]
    return (
        heading,
        kpis,
        _season_figure(g.team_season_summary(played)),
        _split_table(g.team_split(played)),
        to_records(rows.sort_values("date", ascending=False)),
    )


def _season_figure(by_season) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=by_season["season"], y=by_season["points_for"], name="Scored", marker_color=ACCENT
    )
    fig.add_bar(
        x=by_season["season"], y=by_season["points_against"], name="Allowed", marker_color=MUTED
    )
    fig.add_scatter(
        x=by_season["season"],
        y=by_season["win_rate"],
        name="Win rate",
        mode="lines+markers",
        line={"color": INFO, "width": 2.5},
        customdata=by_season[["wins", "losses"]],
        hovertemplate="%{y:.0%} (%{customdata[0]}–%{customdata[1]})<extra>Win rate</extra>",
        secondary_y=True,
    )
    fig.update_yaxes(title="Points per game", secondary_y=False, rangemode="tozero")
    fig.update_yaxes(
        title="Win rate", tickformat=".0%", range=[0, 1.05], secondary_y=True, showgrid=False
    )
    fig.update_xaxes(type="category")  # keep "2010-11" from being parsed as a date
    fig.update_layout(barmode="group", legend={"orientation": "h", "y": -0.2}, hovermode="x")
    return fig


def _split_table(split) -> dbc.Table:
    header = html.Thead(html.Tr([html.Th(""), html.Th("Record"), html.Th("For"), html.Th("Agst")]))
    body = html.Tbody(
        [
            html.Tr(
                [
                    html.Th(r.venue),
                    html.Td(
                        f"{int(r.wins)}–{int(r.games - r.wins)} ({fmt.pct(r.win_rate, 0)})"
                        if r.games == r.games
                        else fmt.DASH
                    ),
                    html.Td(fmt.number(r.points_for, 1)),
                    html.Td(fmt.number(r.points_against, 1)),
                ]
            )
            for r in split.itertuples()
        ]
    )
    return dbc.Table([header, body], className="split-table mb-0", borderless=True)
