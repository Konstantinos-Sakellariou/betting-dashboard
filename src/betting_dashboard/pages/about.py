"""About: methodology, definitions, data coverage and disclaimer."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from betting_dashboard.analytics import betting
from betting_dashboard.analytics import games as g
from betting_dashboard.components.layout import card, page_header
from betting_dashboard.config import settings
from betting_dashboard.data import store

PATH = "/about"
NAME = "About"
TITLE = "About & methodology"
DESCRIPTION = "How the predictions were made and graded, and what the data covers."

METHOD = f"""
### What this is

{settings.app_name} tracks a machine-learning model that predicted the final score of
European and NBA basketball games. From each predicted score it derived two picks:

* **Totals:** *over* or *under* the bookmaker's total-points line.
* **Moneyline:** which team wins.

Every published pick is kept and graded against the final score. Nothing is removed after
the fact.

### The recommended strategy

Bet the **totals pick only when the edge is above {betting.RECOMMENDED_EDGE:g} points**, meaning the
predicted total differs from the bookmaker line by more than that. The original site used this
cut-off for its "Recommended Predictions". In the archive it is the only slice that made money:
smaller edges lose and the biggest edges are too few to trust. The overview opens on this
strategy and shows it next to the full record, so both are always visible. It is still a small
sample, so treat it as a promising edge, not a proven one.

### How picks are graded

| Term | Meaning |
|---|---|
| **Edge** | Points between the predicted total and the line. Equal means no totals pick. |
| **Win / loss / push** | A total landing exactly on the line is a *push*: the stake is returned. |
| **Units** | Profit at a flat 1-unit stake. A win pays `odds − 1`, a loss costs 1. |
| **Hit rate** | Wins ÷ (wins + losses). Pushes are excluded. |
| **ROI** | Units ÷ units staked on decided picks. |
| **Break-even** | The hit rate needed to make zero profit at the average price (1 ÷ odds). |

Moneyline picks use the recorded market-average odds for the picked side. The archive does
not hold over/under prices for the prediction window, so totals are priced at a typical
**{betting.TOTALS_ASSUMED_ODDS:.2f}** (break-even 52.6%).

### The historical dataset

The explorer, team and game-data pages use a separate set of past games with closing
lines, odds from several bookmakers (mean, spread, opening and closing prices), implied
win probabilities and rolling team scoring averages. These were the model's training
features.
"""


def layout(**_query: str) -> html.Div:
    games = store.games()
    preds = store.predictions()
    coverage = (
        games.groupby("league")
        .agg(games=("date", "size"), first=("date", "min"), last=("date", "max"))
        .reindex(g.leagues(games))
        .reset_index()
    )
    coverage_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Competition"), html.Th("Games"), html.Th("Span")])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(r.league),
                            html.Td(f"{r.games:,}"),
                            html.Td(f"{r.first:%Y} – {r.last:%Y}"),
                        ]
                    )
                    for r in coverage.itertuples()
                ]
            ),
        ],
        className="split-table mb-0",
        borderless=True,
        size="sm",
    )
    return html.Div(
        [
            page_header("About & methodology"),
            dbc.Row(
                [
                    dbc.Col(card(dcc.Markdown(METHOD, className="prose")), lg=7),
                    dbc.Col(
                        [
                            card(
                                [
                                    html.P(
                                        f"{len(games):,} games · {len(g.teams(games))} teams · "
                                        f"{len(g.seasons(games))} seasons",
                                        className="muted",
                                    ),
                                    coverage_table,
                                ],
                                title="Data coverage",
                                className="mb-4",
                            ),
                            card(
                                html.P(
                                    f"{len(preds):,} graded predictions from "
                                    f"{preds['date'].min():%d %b %Y} to "
                                    f"{preds['date'].max():%d %b %Y}.",
                                    className="mb-0",
                                ),
                                title="Prediction archive",
                                className="mb-4",
                            ),
                            card(
                                dcc.Markdown(
                                    "This site is for **research and entertainment**. Past "
                                    "results do not predict future ones, and nothing here is "
                                    "betting advice. You must be 18+ (or the legal age where you "
                                    "live) to bet. If gambling stops being fun, free confidential "
                                    "help is available at "
                                    "[BeGambleAware](https://www.begambleaware.org/) and "
                                    "[Gambling Therapy](https://www.gamblingtherapy.org/).",
                                    className="prose",
                                ),
                                title="Play responsibly",
                            ),
                        ],
                        lg=5,
                    ),
                ],
                className="g-4",
            ),
        ]
    )
