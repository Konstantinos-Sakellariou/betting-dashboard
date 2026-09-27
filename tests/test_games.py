import pandas as pd

from betting_dashboard.analytics.games import (
    filter_games,
    leagues,
    season_trends,
    team_games,
    team_season_summary,
    team_split,
)


def _games():
    rows = [
        ("2019-20", "EuroLeague", "Olympiacos", "Real Madrid", 80, 70, 150.5),
        ("2019-20", "Greek Basket League", "AEK", "Olympiacos", 75, 90, 160.5),
        ("2020-21", "EuroLeague", "Real Madrid", "Olympiacos", 85, 84, 169.0),
        ("2020-21", "Liga ACB", "Real Madrid", "Barcelona", 70, 72, 150.0),
    ]
    df = pd.DataFrame(
        rows,
        columns=["season", "league", "home_team", "away_team", "home_score", "away_score", "line"],
    )
    df["date"] = pd.date_range("2020-01-01", periods=len(df))
    df["total_points"] = df.home_score + df.away_score
    df["margin"] = df.home_score - df.away_score
    df["winner"] = df.margin.gt(0).map({True: "home", False: "away"})
    df["total_result"] = ["under", "over", "under", "over"]
    return df


def test_filters_combine_instead_of_overriding():
    # The legacy app dropped the season filter as soon as a league was picked.
    df = _games()
    out = filter_games(df, seasons="2020-21", leagues=["EuroLeague"], team="Olympiacos")
    assert len(out) == 1
    assert out.iloc[0].home_team == "Real Madrid"


def test_empty_filters_mean_all():
    assert len(filter_games(_games(), seasons=[], leagues=None, team=None)) == 4


def test_leagues_follow_display_order():
    assert leagues(_games()) == ["EuroLeague", "Liga ACB", "Greek Basket League"]


def test_team_games_perspective():
    t = team_games(_games(), "Olympiacos")
    assert t.venue.tolist() == ["Home", "Away", "Away"]
    assert t.points_for.tolist() == [80, 90, 84]
    assert t.won.tolist() == [True, True, False]
    split = team_split(t).set_index("venue")
    assert split.loc["Home", "wins"] == 1
    assert split.loc["Away", "games"] == 2
    by_season = team_season_summary(t).set_index("season")
    assert by_season.loc["2020-21", "losses"] == 1


def test_season_trends():
    trends = season_trends(_games()).set_index(["league", "season"])
    assert trends.loc[("EuroLeague", "2019-20"), "avg_total"] == 150
    assert trends.loc[("EuroLeague", "2020-21"), "home_win_rate"] == 1.0
