# Courtside Analytics: basketball betting dashboard

[![Live demo](https://img.shields.io/badge/live_demo-betting--dashboard.onrender.com-f59e0b?style=flat)](https://betting-dashboard.onrender.com)
[![CI](https://github.com/Konstantinos-Sakellariou/betting-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Konstantinos-Sakellariou/betting-dashboard/actions/workflows/ci.yml)

**Live demo: [betting-dashboard.onrender.com](https://betting-dashboard.onrender.com)**

![A 30-second tour: the recommended strategy against all picks, predictions, the league explorer and a team profile](docs/demo.gif)

This dashboard shows how a basketball score-prediction model performed across EuroLeague, EuroCup, the NBA and nine European domestic leagues. It includes 35,000 historical games you can explore.

- **The recommended strategy comes first.** Betting the totals pick only when the model's predicted total differs from the line by more than 2.5 points returned **+3.5% ROI (+6.3 units) over 180 picks**. The overview opens on it.
- **The track record is honest.** All 1,292 published picks are graded against the final score, and the full record (−4.1% ROI on every totals pick) is always shown next to the strategy, each against its break-even point.
- **Predictions show each game's forecast.** You see the predicted score, the over/under pick against the bookmaker line, and the moneyline pick.
- **The league explorer** covers scoring trends, home advantage, and a scatter plot of any two variables across 11 leagues and 11 seasons (2010–2021).
- **Team profiles** show a team's record, points for and against by season, home/away splits, and over/under history.
- **Game data** is a searchable table of every game, with odds and lines. Rows load from the server as you scroll, and you can export to CSV.

| Predictions | Explorer | Teams |
|---|---|---|
| ![](docs/screenshots/predictions.png) | ![](docs/screenshots/explorer.png) | ![](docs/screenshots/teams.png) |

## Quick start

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.13 for you if it's missing.

```bash
uv sync                                   # create .venv from uv.lock
uv run python -m betting_dashboard.app    # http://localhost:8050
```

Or run it with Docker:

```bash
docker build -t betting-dashboard .
docker run -p 8050:8050 betting-dashboard
```

## Development

```bash
uv run pytest                      # unit + app smoke tests
uv run ruff check . && uv run ruff format .
uv run python scripts/build_data.py   # rebuild data/processed from data/raw
```

CI runs the same steps on every push. It also checks that `data/processed` rebuilds byte-for-byte from `data/raw`, and it builds and smoke-tests the Docker image.

### Project layout

```
src/betting_dashboard/
  app.py            Dash app factory; gunicorn serves betting_dashboard.app:server
  config.py         settings from environment variables (see .env.example)
  data/             schema contracts, cleaning rules, cached loaders
  analytics/        pure functions: pick grading, ROI, team/league aggregates, grid queries
  components/       navbar/footer, KPI cards, AG Grid defaults, Plotly theme
  pages/            overview, predictions, explorer, teams, games, about
  assets/           CSS, favicon, vendored Bootstrap/icons/Inter (no third-party requests)
data/raw/           original CSVs (gzipped, untouched)
data/processed/     cleaned Parquet files the app reads
docs/               revival plan, data dictionary, screenshots
```

## Deployment

The repo includes a [Render Blueprint](render.yaml). In Render, choose **New + → Blueprint** and select this repository. It builds the Dockerfile, checks `/healthz`, and redeploys on every push to `main`. Any other container host works too. The app listens on `$PORT`.

**Keep-alive.** Render's free plan puts the service to sleep after about 15 idle minutes, and the next visitor waits 30–60 s for it to wake. The [keep-alive workflow](.github/workflows/keepalive.yml) pings `/healthz` every 10 minutes from 06:00 to 21:59 UTC. To point it at another URL, set a `SITE_URL` repository variable; to pause it, disable the workflow in the Actions tab. GitHub switches off scheduled workflows after 60 days without repository activity, so re-enable it there if that happens.

**Demo GIF.** `docs/demo.gif` is recorded by [`scripts/record_demo.py`](scripts/record_demo.py). Start the app, run `uv run --group demo playwright install chromium` once, then run `uv run --group demo python scripts/record_demo.py`.

## Documentation

- [docs/REVIVAL_PLAN.md](docs/REVIVAL_PLAN.md): audit of the legacy app, target architecture, roadmap and open questions.
- [docs/DATA.md](docs/DATA.md): data dictionary, cleaning rules and metric definitions.
- [docs/BACKLOG.md](docs/BACKLOG.md): next tasks, each with a ready-to-use prompt for Claude.

## License

The code is released under the [MIT License](LICENSE). The historical odds and results in `data/` are included for research and education only.

## Disclaimer

This project is for research and entertainment. Past results do not predict future ones, and nothing here is betting advice. 18+ only. If gambling stops being fun, visit [BeGambleAware](https://www.begambleaware.org/).
