"""League explorer: scoring trends, home advantage and a free-form feature scatter."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, html

from betting_dashboard.analytics import games as g
from betting_dashboard.components.layout import (
    card,
    dropdown,
    empty_figure,
    field,
    graph,
    page_header,
)
from betting_dashboard.components.theme import ACCENT, LOSS, MUTED, PUSH, WIN
from betting_dashboard.data import store
from betting_dashboard.data.schema import FEATURE_LABELS

PATH = "/explorer"
NAME = "Explorer"
TITLE = "League explorer"
DESCRIPTION = "Scoring trends, home advantage and odds across 11 basketball leagues, 2010–2021."

SCATTER_SAMPLE = 6000
COLOR_OPTIONS = {
    "league": "Competition",
    "winner": "Winner",
    "total_result": "Over / under",
    "season": "Season",
}
OUTCOME_COLORS = {"home": ACCENT, "away": "#38bdf8", "over": WIN, "under": LOSS, "push": PUSH}


def layout(**_query: str) -> html.Div:
    games = store.games()
    feature_opts = [{"label": v, "value": k} for k, v in FEATURE_LABELS.items()]
    filters = dbc.Row(
        [
            field(
                "Seasons",
                dropdown("ex-seasons", g.seasons(games), multi=True, placeholder="All seasons"),
            ),
            field(
                "Competitions",
                dropdown(
                    "ex-leagues", g.leagues(games), multi=True, placeholder="All competitions"
                ),
                {"xs": 12, "md": 6, "lg": 5},
            ),
            field(
                "Colour by",
                dropdown(
                    "ex-color",
                    [{"label": v, "value": k} for k, v in COLOR_OPTIONS.items()],
                    "league",
                    clearable=False,
                ),
                {"xs": 12, "md": 6, "lg": 4},
            ),
        ],
        className="g-3",
    )
    axes = dbc.Row(
        [
            field(
                "X axis",
                dropdown("ex-x", feature_opts, "line", clearable=False),
                {"xs": 12, "md": 6},
            ),
            field(
                "Y axis",
                dropdown("ex-y", feature_opts, "total_points", clearable=False),
                {"xs": 12, "md": 6},
            ),
        ],
        className="g-3 mb-2",
    )
    return html.Div(
        [
            page_header(
                "League explorer",
                f"{len(games):,} games from {games['date'].min():%Y} to {games['date'].max():%Y}. "
                "The filters apply to every chart on this page.",
            ),
            card(filters, className="mb-4"),
            html.Div(id="ex-count", className="muted small mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        card(
                            graph("ex-trend", height=360),
                            title="Scoring trend",
                            subtitle="Average total points per game by season.",
                        ),
                        lg=7,
                    ),
                    dbc.Col(
                        card(
                            graph("ex-home", height=360),
                            title="Home advantage",
                            subtitle="Share of games won by the home team.",
                        ),
                        lg=5,
                    ),
                ],
                className="g-4 mb-4",
            ),
            card(
                [axes, graph("ex-scatter", height=480)],
                title="Feature scatter",
                subtitle=f"Compare any two variables. Large selections are sampled to "
                f"{SCATTER_SAMPLE:,} points.",
                className="mb-4",
            ),
        ]
    )


@callback(
    Output("ex-count", "children"),
    Output("ex-trend", "figure"),
    Output("ex-home", "figure"),
    Input("ex-seasons", "value"),
    Input("ex-leagues", "value"),
)
def update_league_charts(seasons, leagues):
    df = g.filter_games(store.games(), seasons=seasons, leagues=leagues)
    count = f"{len(df):,} games match the current filters."
    if df.empty:
        empty = empty_figure("No games match these filters.")
        return count, empty, empty

    trends = g.season_trends(df)
    order = [lg for lg in g.leagues(df)]
    trend_fig = px.line(
        trends,
        x="season",
        y="avg_total",
        color="league",
        category_orders={"league": order, "season": sorted(trends["season"].unique())},
        markers=True,
        labels={"season": "Season", "avg_total": "Avg. total points", "league": ""},
        custom_data=["games", "over_rate"],
    )
    trend_fig.update_traces(
        hovertemplate="%{x}<br>%{y:.1f} pts/game<br>%{customdata[0]} games · "
        "over %{customdata[1]:.0%}<extra>%{fullData.name}</extra>"
    )
    # Season labels like "2010-11" would otherwise be parsed as dates.
    trend_fig.update_xaxes(type="category")
    trend_fig.update_layout(legend={"orientation": "h", "y": -0.25}, hovermode="closest")

    summary = g.league_summary(df).sort_values("home_win_rate")
    home_fig = go.Figure(
        go.Bar(
            x=summary["home_win_rate"],
            y=summary["league"],
            orientation="h",
            marker_color=ACCENT,
            text=[f"{v:.0%}" for v in summary["home_win_rate"]],
            textposition="inside",
            insidetextanchor="end",
            textfont={"color": "#111", "size": 12},
            customdata=summary[["games", "avg_margin"]],
            hovertemplate="%{y}<br>Home wins %{x:.1%}<br>Avg. home margin "
            "%{customdata[1]:+.1f}<br>%{customdata[0]:,} games<extra></extra>",
        )
    )
    home_fig.add_vline(x=0.5, line_dash="dot", line_color=MUTED)
    home_fig.update_xaxes(tickformat=".0%", range=[0, 1])
    home_fig.update_layout(margin={"l": 8}, yaxis={"automargin": True})
    return count, trend_fig, home_fig


@callback(
    Output("ex-scatter", "figure"),
    Input("ex-seasons", "value"),
    Input("ex-leagues", "value"),
    Input("ex-x", "value"),
    Input("ex-y", "value"),
    Input("ex-color", "value"),
)
def update_scatter(seasons, leagues, x, y, color):
    df = g.filter_games(store.games(), seasons=seasons, leagues=leagues)
    if df.empty or not x or not y:
        return empty_figure("No games match these filters.")
    if len(df) > SCATTER_SAMPLE:
        df = df.sample(SCATTER_SAMPLE, random_state=0)
    color = color or "league"
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        render_mode="webgl",
        opacity=0.55,
        labels={**FEATURE_LABELS, **COLOR_OPTIONS},
        category_orders={"league": g.leagues(df), "season": sorted(df["season"].unique())},
        color_discrete_map=OUTCOME_COLORS if color in {"winner", "total_result"} else None,
        hover_data={
            "date": "|%d %b %Y",
            "home_team": True,
            "away_team": True,
            "home_score": True,
            "away_score": True,
            "league": color != "league",
        },
    )
    fig.update_traces(marker={"size": 6})
    fig.update_layout(legend={"title": None, "itemsizing": "constant"})
    return fig
