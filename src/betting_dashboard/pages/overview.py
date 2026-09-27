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
DESCRIPTION = (
    "The recommended strategy: basketball totals picks with an edge above "
    f"{betting.RECOMMENDED_EDGE:g} points, graded against every published prediction."
)

MIN_LEAGUE_PICKS = 10
EDGE_MARKS = {v: f"{v:g}" for v in [0, 1, 2, 3, 4, 5]} | {
    betting.RECOMMENDED_EDGE: {"label": "2.5 ★", "style": {"color": ACCENT, "fontWeight": 700}}
}


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
                            "Only count games where the model's predicted total differs from "
                            "the bookmaker line by more than this many points. The ★ marks the "
                            f"recommended cut-off of {betting.RECOMMENDED_EDGE:g}, which the "
                            "original site used for its 'Recommended Predictions'. Set it to 0 "
                            "to see every pick.",
                            target="ov-edge-help",
                        ),
                        dcc.Slider(
                            id="ov-edge",
                            min=0,
                            max=5,
                            step=0.5,
                            value=betting.RECOMMENDED_EDGE,
                            marks=EDGE_MARKS,
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
                [
                    "The recommended strategy is to bet the ",
                    html.Strong("totals pick"),
                    " only when the predicted total differs from the bookmaker line by more "
                    f"than {betting.RECOMMENDED_EDGE:g} points. Every figure is graded from "
                    f"{len(preds):,} published predictions across {n_leagues} competitions "
                    f"({first:%d %b %Y} – {last:%d %b %Y}), at a flat 1-unit stake.",
                ],
            ),
            card(controls, className="mb-3"),
            html.Div(id="ov-compare", className="compare-strip mb-4"),
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
                title="Why 2.5 points? Totals ROI by edge threshold",
                subtitle="Totals ROI for picks above each edge threshold. Bar labels show "
                "how many picks qualify.",
                className="mb-4",
            ),
            html.P(id="ov-footnote", className="footnote"),
        ]
    )


def view_label(min_edge: float | None) -> str:
    if not min_edge:
        return "All picks"
    if min_edge == betting.RECOMMENDED_EDGE:
        return "Recommended strategy"
    return f"Custom: edge > {min_edge:g}"


def _compare_strip(market: str, min_edge: float | None) -> list:
    preds = store.predictions()
    views = [("Recommended strategy", betting.RECOMMENDED_EDGE), ("All picks", 0)]
    if min_edge and min_edge != betting.RECOMMENDED_EDGE:
        views.insert(0, (f"Custom: edge > {min_edge:g}", min_edge))
    active = view_label(min_edge)
    items = []
    for label, edge in views:
        rec = betting.record(betting.with_min_edge(preds, edge), market)
        items.append(
            html.Div(
                [
                    html.Div(
                        [label, html.Span("Showing", className="compare-tag")]
                        if label == active
                        else label,
                        className="compare-label",
                    ),
                    html.Div(
                        [
                            html.Span(
                                f"{fmt.signed_pct(rec.roi)} ROI",
                                className=f"tone-{fmt.tone(rec.roi)} fw-bold",
                            ),
                            f" · {fmt.units(rec.units)} · {rec.picks:,} picks · "
                            f"{fmt.pct(rec.hit_rate)} hit rate",
                        ],
                        className="compare-value",
                    ),
                ],
                className="compare-item" + (" compare-item-active" if label == active else ""),
            )
        )
    return items


@callback(
    Output("ov-compare", "children"),
    Output("ov-kpis", "children"),
    Output("ov-cumulative", "figure"),
    Output("ov-leagues", "figure"),
    Output("ov-footnote", "children"),
    Input("ov-market", "value"),
    Input("ov-edge", "value"),
)
def update_overview(market: str, min_edge: float | None):
    preds = betting.with_min_edge(store.predictions(), min_edge)
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
        "The edge filter selects games, so it applies to both markets; the recommended strategy "
        "is the totals market. Totals picks are priced at an assumed 1.90 because the archive "
        "holds no over/under prices for the prediction window. Moneyline picks use the recorded "
        "market-average odds. Pushes return the stake and are excluded from hit rate and ROI. "
        f"The recommended sample is {_recommended_sample():,} totals picks, which is small: "
        "treat the edge as promising, not proven."
    )
    return (
        _compare_strip(market, min_edge),
        kpis,
        _cumulative_figure(preds, market),
        _league_figure(preds, market),
        footnote,
    )


@callback(Output("ov-edge-curve", "figure"), Input("ov-market", "value"))
def update_edge_curve(_market: str):
    thresholds = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
    curve = betting.edge_curve(store.predictions(), thresholds)
    fig = go.Figure(
        go.Bar(
            x=[f"> {t:g}" for t in curve["threshold"]],
            y=curve["roi"],
            marker_color=[WIN if v > 0 else LOSS for v in curve["roi"].fillna(0)],
            marker_line_color=[
                ACCENT if t == betting.RECOMMENDED_EDGE else "rgba(0,0,0,0)"
                for t in curve["threshold"]
            ],
            marker_line_width=3,
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
    fig.add_annotation(
        x=f"> {betting.RECOMMENDED_EDGE:g}",
        y=1.08,
        yref="paper",
        text="★ Recommended",
        showarrow=False,
        font={"color": ACCENT, "size": 12},
    )
    fig.update_layout(margin={"t": 40})
    return fig


def _recommended_sample() -> int:
    recommended = betting.with_min_edge(store.predictions(), betting.RECOMMENDED_EDGE)
    return betting.record(recommended, "total").picks


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
