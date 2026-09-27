"""Overview: the model's track record at a glance."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from betting_dashboard.analytics import betting
from betting_dashboard.components import format as fmt
from betting_dashboard.components.layout import card, empty_figure, graph, kpi, page_header
from betting_dashboard.components.theme import ACCENT, BORDER, LOSS, MUTED, WIN
from betting_dashboard.data import store

PATH = "/"
NAME = "Overview"
TITLE = "Track record"
DESCRIPTION = "How a basketball prediction model performed on 1,292 published picks."

MIN_LEAGUE_PICKS = 10
EDGE_MARKS = {v: f"{v:g}" for v in [0, 1, 2, 2.5, 3, 4, 5]}


def layout(**_query: str) -> html.Div:
    preds = store.predictions()
    first, last = preds["date"].min(), preds["date"].max()
    n_leagues = preds["league"].nunique()

    controls = dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        dbc.Label("Market", className="field-label"),
                        dbc.RadioItems(
                            id="ov-market",
                            options=[{"label": v, "value": k} for k, v in betting.MARKETS.items()],
                            value="total",
                            inline=True,
                            className="segmented",
                            inputClassName="btn-check",
                            labelClassName="btn btn-segment",
                            labelCheckedClassName="active",
                        ),
                    ],
                    className="field",
                ),
                xs=12,
                lg=5,
            ),
            dbc.Col(
                html.Div(
                    [
                        dbc.Label(
                            [
                                "Minimum edge (points between predicted total and line) ",
                                html.Span("?", id="ov-edge-help", className="help-dot"),
                            ],
                            className="field-label",
                        ),
                        dbc.Tooltip(
                            "Only count totals picks where the model's predicted total differs "
                            "from the bookmaker line by more than this many points. 2.5 was the "
                            "cut-off for the original 'recommended' picks.",
                            target="ov-edge-help",
                        ),
                        dcc.Slider(
                            id="ov-edge",
                            min=0,
                            max=5,
                            step=0.5,
                            value=0,
                            marks=EDGE_MARKS,
                            persistence=True,
                            persistence_type="session",
                        ),
                    ],
                    className="field",
                ),
                xs=12,
                lg=7,
            ),
        ],
        className="g-3 mb-3",
    )

    return html.Div(
        [
            page_header(
                "Model track record",
                f"{len(preds):,} graded predictions across {n_leagues} competitions, "
                f"{first:%d %b %Y} – {last:%d %b %Y}. Profit is shown in units at a flat "
                "1-unit stake.",
            ),
            card(controls, className="mb-4"),
            dbc.Row(id="ov-kpis", className="g-3 mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        card(
                            graph("ov-cumulative", height=340),
                            title="Cumulative profit",
                            subtitle="Running total of units won or lost, by match day.",
                        ),
                        lg=7,
                    ),
                    dbc.Col(
                        card(
                            graph("ov-leagues", height=340),
                            title="ROI by competition",
                            subtitle=f"Competitions with at least {MIN_LEAGUE_PICKS} picks.",
                        ),
                        lg=5,
                    ),
                ],
                className="g-4 mb-4",
            ),
            card(
                graph("ov-edge-curve", height=300),
                title="Does a bigger edge mean better totals picks?",
                subtitle="Totals ROI for picks above each edge threshold. Bar labels show "
                "how many picks qualify.",
                className="mb-4",
            ),
            html.P(id="ov-footnote", className="footnote"),
        ]
    )


def _filtered(market: str, min_edge: float) -> pd.DataFrame:
    preds = store.predictions()
    if market == "total" and min_edge:
        preds = preds[preds["edge"] > min_edge]
    return preds


@callback(Output("ov-edge", "disabled"), Input("ov-market", "value"))
def disable_edge_for_moneyline(market: str) -> bool:
    return market != "total"


@callback(
    Output("ov-kpis", "children"),
    Output("ov-cumulative", "figure"),
    Output("ov-leagues", "figure"),
    Output("ov-footnote", "children"),
    Input("ov-market", "value"),
    Input("ov-edge", "value"),
)
def update_overview(market: str, min_edge: float):
    preds = _filtered(market, min_edge or 0)
    rec = betting.record(preds, market)

    hit_vs_be = rec.hit_rate - rec.break_even if rec.decided else float("nan")
    kpis = [
        dbc.Col(
            kpi(
                "Picks",
                fmt.number(rec.picks),
                f"{rec.wins} W · {rec.losses} L · {rec.pushes} P",
            ),
            xs=6,
            lg=3,
        ),
        dbc.Col(
            kpi(
                "Hit rate",
                fmt.pct(rec.hit_rate),
                f"Break-even {fmt.pct(rec.break_even)} ({fmt.signed_points(hit_vs_be)})",
                tone=fmt.tone(hit_vs_be),
            ),
            xs=6,
            lg=3,
        ),
        dbc.Col(
            kpi("Profit", fmt.units(rec.units), "at 1 unit per pick", tone=fmt.tone(rec.units)),
            xs=6,
            lg=3,
        ),
        dbc.Col(
            kpi(
                "ROI",
                fmt.signed_pct(rec.roi),
                f"avg. odds {fmt.number(rec.avg_odds, 2)}",
                tone=fmt.tone(rec.roi),
            ),
            xs=6,
            lg=3,
        ),
    ]

    footnote = (
        "Totals picks are priced at an assumed 1.90 because the archive holds no over/under "
        "prices for the prediction window. Moneyline picks use the recorded market-average "
        "odds. Pushes return the stake and are excluded from hit rate and ROI."
    )
    return kpis, _cumulative_figure(preds, market), _league_figure(preds, market), footnote


@callback(Output("ov-edge-curve", "figure"), Input("ov-market", "value"))
def update_edge_curve(_market: str):
    thresholds = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
    curve = betting.edge_curve(store.predictions(), thresholds)
    fig = go.Figure(
        go.Bar(
            x=[f"> {t:g}" for t in curve["threshold"]],
            y=curve["roi"],
            marker_color=[WIN if v > 0 else LOSS for v in curve["roi"].fillna(0)],
            text=[f"{n} picks" for n in curve["picks"]],
            textposition="outside",
            cliponaxis=False,
            customdata=curve[["hit_rate", "picks"]],
            hovertemplate="Edge %{x}<br>ROI %{y:+.1%}<br>Hit rate %{customdata[0]:.1%}"
            "<br>%{customdata[1]} picks<extra></extra>",
        )
    )
    fig.update_yaxes(tickformat="+.0%", title="ROI")
    fig.update_xaxes(title="Edge (points)")
    fig.add_hline(y=0, line_color=BORDER)
    return fig


def _cumulative_figure(preds: pd.DataFrame, market: str) -> go.Figure:
    daily = betting.cumulative_units(preds, market)
    if daily.empty:
        return empty_figure("No picks match these settings.")
    final = daily["cumulative_units"].iloc[-1]
    color = WIN if final >= 0 else LOSS
    fig = go.Figure(
        go.Scatter(
            x=daily["date"],
            y=daily["cumulative_units"],
            mode="lines",
            line={"color": color, "width": 2.5, "shape": "hv"},
            fill="tozeroy",
            fillcolor=f"rgba({_rgb(color)},0.12)",
            customdata=daily[["picks", "units"]],
            hovertemplate="%{x|%d %b %Y}<br>Total %{y:+.1f}u<br>"
            "Day: %{customdata[1]:+.2f}u from %{customdata[0]} picks<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color=MUTED, line_dash="dot")
    fig.update_yaxes(title="Units", ticksuffix="u")
    fig.update_layout(showlegend=False, hovermode="x")
    return fig


def _league_figure(preds: pd.DataFrame, market: str) -> go.Figure:
    table = betting.record_by(preds, "league", market)
    table = table[table["picks"] >= MIN_LEAGUE_PICKS].sort_values("roi")
    if table.empty:
        return empty_figure("Not enough picks per competition.")
    fig = go.Figure(
        go.Bar(
            x=table["roi"],
            y=table["league"],
            orientation="h",
            marker_color=[WIN if v > 0 else LOSS for v in table["roi"]],
            customdata=table[["picks", "hit_rate", "units"]],
            hovertemplate="%{y}<br>ROI %{x:+.1%}<br>Hit rate %{customdata[1]:.1%}"
            "<br>%{customdata[2]:+.1f}u from %{customdata[0]} picks<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor=ACCENT)
    fig.update_layout(margin={"l": 8}, yaxis={"automargin": True})
    return fig


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return ",".join(str(int(h[i : i + 2], 16)) for i in (0, 2, 4))
