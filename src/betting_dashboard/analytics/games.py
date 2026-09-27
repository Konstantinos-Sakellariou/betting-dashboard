"""Filtering and aggregates over the historical games table."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from betting_dashboard.data.schema import LEAGUE_ORDER


def _as_list(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def filter_games(
    df: pd.DataFrame,
    seasons: str | Iterable[str] | None = None,
    leagues: str | Iterable[str] | None = None,
    team: str | None = None,
) -> pd.DataFrame:
    """Apply every given filter together. Empty/None means 'all'."""
    mask = pd.Series(True, index=df.index)
    if seasons := _as_list(seasons):
        mask &= df["season"].isin(seasons)
    if leagues := _as_list(leagues):
        mask &= df["league"].isin(leagues)
    if team:
        mask &= df["home_team"].eq(team) | df["away_team"].eq(team)
    return df[mask]


def seasons(df: pd.DataFrame) -> list[str]:
    return sorted(df["season"].unique(), reverse=True)


def leagues(df: pd.DataFrame) -> list[str]:
    present = set(df["league"].unique())
    return [lg for lg in LEAGUE_ORDER if lg in present] + sorted(present - set(LEAGUE_ORDER))


def teams(df: pd.DataFrame, league: str | None = None) -> list[str]:
    if league:
        df = df[df["league"].eq(league)]
    return sorted(set(df["home_team"]) | set(df["away_team"]))


def team_primary_league(df: pd.DataFrame, team: str) -> str:
    """The league a team played most games in (a team can appear in several)."""
    played = filter_games(df, team=team)
    return played["league"].value_counts().idxmax()


def season_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Per league and season: games, avg total points, avg line, home-win and over rates."""
    decided = df.assign(
        home_win=df["winner"].eq("home"),
        over=df["total_result"].eq("over"),
    )
    return (
        decided.groupby(["league", "season"], observed=True)
        .agg(
            games=("total_points", "size"),
            avg_total=("total_points", "mean"),
            avg_line=("line", "mean"),
            home_win_rate=("home_win", "mean"),
            over_rate=("over", "mean"),
        )
        .reset_index()
    )


def league_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per league with overall averages, sorted by home-win rate."""
    summary = (
        df.assign(home_win=df["winner"].eq("home"), over=df["total_result"].eq("over"))
        .groupby("league", observed=True)
        .agg(
            games=("total_points", "size"),
            avg_total=("total_points", "mean"),
            home_win_rate=("home_win", "mean"),
            over_rate=("over", "mean"),
            avg_margin=("margin", "mean"),
        )
        .reset_index()
    )
    return summary.sort_values("home_win_rate", ascending=False).reset_index(drop=True)


def team_games(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Every game `team` played, from the team's point of view."""
    played = filter_games(df, team=team).copy()
    at_home = played["home_team"].eq(team)
    played["venue"] = at_home.map({True: "Home", False: "Away"})
    played["opponent"] = played["away_team"].where(at_home, played["home_team"])
    played["points_for"] = played["home_score"].where(at_home, played["away_score"])
    played["points_against"] = played["away_score"].where(at_home, played["home_score"])
    played["won"] = played["points_for"] > played["points_against"]
    return played.sort_values("date")


def team_season_summary(team_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the output of `team_games` per season."""
    return (
        team_df.assign(over=team_df["total_result"].eq("over"))
        .groupby("season", observed=True)
        .agg(
            games=("won", "size"),
            wins=("won", "sum"),
            points_for=("points_for", "mean"),
            points_against=("points_against", "mean"),
            over_rate=("over", "mean"),
        )
        .assign(losses=lambda x: x["games"] - x["wins"], win_rate=lambda x: x["wins"] / x["games"])
        .reset_index()
    )


def team_split(team_df: pd.DataFrame) -> pd.DataFrame:
    """Home vs away record for the output of `team_games`."""
    return (
        team_df.groupby("venue")
        .agg(
            games=("won", "size"),
            wins=("won", "sum"),
            points_for=("points_for", "mean"),
            points_against=("points_against", "mean"),
        )
        .assign(win_rate=lambda x: x["wins"] / x["games"])
        .reindex(["Home", "Away"])
        .reset_index()
    )
