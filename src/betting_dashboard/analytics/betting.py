"""Grading picks and measuring a betting track record.

Two markets are tracked for every predicted game:

* ``ml``    - moneyline: which side wins. Priced at the recorded market mean odds.
* ``total`` - over/under the points line. The archive holds no totals prices for the
  prediction window, so a standard price of ``TOTALS_ASSUMED_ODDS`` is used.

All profit figures are in units at a flat 1-unit stake.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np
import pandas as pd

Market = Literal["ml", "total"]
MARKETS: dict[Market, str] = {"total": "Totals (over/under)", "ml": "Moneyline"}

TOTALS_ASSUMED_ODDS = 1.90
# The recommended strategy: only bet when the predicted total differs from the line by
# more than this many points. It was the original app's cut-off, and the archive bears it out.
RECOMMENDED_EDGE = 2.5


def grade_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Add result/odds/units columns for both markets to a prediction archive."""
    out = df.copy()
    total = out["home_score"] + out["away_score"]
    out["total_points"] = total

    home_won = out["home_score"] > out["away_score"]
    picked_home = out["ml_pick"].eq("home")
    out["ml_odds"] = np.where(picked_home, out["odd_home"], out["odd_away"])
    ml_win = picked_home == home_won
    out["ml_result"] = pd.Series(np.where(ml_win, "win", "loss"), index=out.index, dtype="str")
    out["ml_units"] = np.where(ml_win, out["ml_odds"] - 1, -1.0)

    has_pick = out["total_pick"].notna()
    went_over = total > out["line"]
    push = total == out["line"]
    total_win = (out["total_pick"] == "over") == went_over
    result = np.select([~has_pick, push, total_win], [None, "push", "win"], default="loss")
    out["total_result"] = pd.Series(result, index=out.index, dtype="str")
    out["total_odds"] = np.where(has_pick, TOTALS_ASSUMED_ODDS, np.nan)
    out["total_units"] = np.select(
        [~has_pick, push, total_win], [np.nan, 0.0, TOTALS_ASSUMED_ODDS - 1], default=-1.0
    )
    return out


@dataclass(frozen=True)
class Record:
    picks: int
    wins: int
    losses: int
    pushes: int
    units: float
    avg_odds: float

    @property
    def decided(self) -> int:
        return self.wins + self.losses

    @property
    def hit_rate(self) -> float:
        return self.wins / self.decided if self.decided else float("nan")

    @property
    def roi(self) -> float:
        """Units won per unit staked; pushes return the stake so they are not counted."""
        return self.units / self.decided if self.decided else float("nan")

    @property
    def break_even(self) -> float:
        """Hit rate needed to break even at the average price."""
        return 1 / self.avg_odds if self.avg_odds else float("nan")

    def as_dict(self) -> dict[str, float]:
        return {
            **asdict(self),
            "hit_rate": self.hit_rate,
            "roi": self.roi,
            "break_even": self.break_even,
        }


def graded(df: pd.DataFrame, market: Market) -> pd.DataFrame:
    """Rows that carry a pick in `market`."""
    return df[df[f"{market}_result"].notna()]


def record(df: pd.DataFrame, market: Market) -> Record:
    bets = graded(df, market)
    results = bets[f"{market}_result"]
    return Record(
        picks=len(bets),
        wins=int(results.eq("win").sum()),
        losses=int(results.eq("loss").sum()),
        pushes=int(results.eq("push").sum()),
        units=float(bets[f"{market}_units"].sum()),
        avg_odds=float(bets[f"{market}_odds"].mean()) if len(bets) else float("nan"),
    )


def record_by(df: pd.DataFrame, by: str, market: Market) -> pd.DataFrame:
    """One `record` row per group, sorted by number of picks."""
    rows = [
        {by: key, **record(group, market).as_dict()}
        for key, group in df.groupby(by, observed=True, sort=False)
    ]
    columns = [by, *Record.__dataclass_fields__, "hit_rate", "roi", "break_even"]
    table = pd.DataFrame(rows, columns=columns)
    return table.sort_values("picks", ascending=False, kind="stable").reset_index(drop=True)


def cumulative_units(df: pd.DataFrame, market: Market) -> pd.DataFrame:
    """Daily running profit: columns date, picks, units, cumulative_units."""
    bets = graded(df, market)
    daily = (
        bets.groupby("date")
        .agg(picks=(f"{market}_units", "size"), units=(f"{market}_units", "sum"))
        .reset_index()
    )
    daily["cumulative_units"] = daily["units"].cumsum()
    return daily


def with_min_edge(df: pd.DataFrame, min_edge: float | None) -> pd.DataFrame:
    """Games whose edge is strictly above `min_edge`. 0 or None keeps every game."""
    return df[df["edge"] > min_edge] if min_edge else df


def edge_curve(df: pd.DataFrame, thresholds: list[float]) -> pd.DataFrame:
    """Totals record for picks with edge strictly above each threshold."""
    rows = [{"threshold": t, **record(df[df["edge"] > t], "total").as_dict()} for t in thresholds]
    return pd.DataFrame(rows)
