# Revival Plan: Betting Dashboard

**Status:** Phases 0–3 are done on branch `claude/zen-sagan-i79dgv`. The owner chose a showcase first, so Phase 4 (live predictions) is deferred. Phases 5–6 are the backlog. See [§11](#11-owner-decisions-and-open-questions).
**Last updated:** 2026-09-27

This document audits the parked project, sets out what it should become, and lays out the steps to get there. It is meant to stay accurate: when the plan changes, update this file in the same commit.

---

## Contents

1. [Executive summary](#1-executive-summary)
2. [Audit of the current state](#2-audit-of-the-current-state)
3. [Goals and principles](#3-goals-and-principles)
4. [Target architecture](#4-target-architecture)
5. [Product and UI redesign](#5-product-and-ui-redesign)
6. [Data and analytics](#6-data-and-analytics)
7. [Deployment and operations](#7-deployment-and-operations)
8. [Roadmap](#8-roadmap)
9. [Phase 4: bringing the prediction pipeline back](#9-phase-4-bringing-the-prediction-pipeline-back)
10. [Risks, legal and responsible-gambling notes](#10-risks-legal-and-responsible-gambling-notes)
11. [Owner decisions and open questions](#11-owner-decisions-and-open-questions)
12. [Decision log](#12-decision-log)

---

## 1. Executive summary

The dashboard (Dash 1.19, Python 3.7, last real change in 2022) **does not start today**. The three CSV files it reads at import time were deleted from the repository in December 2022, so the deployed site at `betting-dashboard.onrender.com` can only crash. Even with the data back, the stack is end-of-life. Python 3.7 reached end of life in 2023, the `dash_core_components` imports and `DataFrame.append` no longer exist, and the pinned `requirements.txt` includes a Windows-only package (`wincertstore`) plus packages the app never uses (`selenium`, `matplotlib`, `scikit-learn`).

The underlying idea is still good: 35k historical basketball games across 11 leagues and 11 seasons, plus a 1,300-game track record of published predictions. It just needs a professional shell. The plan:

1. **Rescue** the data from git history, fix the data-quality bugs in it, and store it as small, typed Parquet files.
2. **Rebuild** the app as a proper Python package on current Dash 4, with pure, tested analytics functions kept separate from the UI.
3. **Redesign** the UI around one question a visitor actually has: *"Is this model any good, and what does it say?"* That means a track-record overview with ROI (not just accuracy), browsable predictions, a data explorer, team pages, and an About/methodology page with a responsible-gambling disclaimer.
4. **Ship it properly**: Docker image, Render blueprint, GitHub Actions CI (lint, tests, image build), and a README with screenshots.
5. **Then** (Phase 4, needs owner input) revive the scraper and model so the site shows live predictions again, refreshed on a schedule.

Phases 1–3 make the project shareable as a *portfolio-quality historical analytics app* even if live predictions never return. Phase 4 turns it back into a *live product*.

---

## 2. Audit of the current state

### 2.1 Inventory

| Path | What it is | Verdict |
|---|---|---|
| `app.py` (330 lines) | App object, routing, all callbacks | Rewrite. About 250 of the lines are one table definition copy-pasted 8 times |
| `assets/functions_and_datasets.py` | Loads CSVs at import time and computes all stats | Split into `data/` (loading/cleaning) and `analytics/` (metrics) |
| `assets/home_page.py`, `statistics_page.py`, `predictions_page.py` | Page layouts | Rewrite as Dash Pages |
| `assets/header.py`, `footer.py` | Banner of NBA/EuroLeague player photos, personal photo, email | Replace with a clean navbar and footer |
| `assets/images/*` | 7 images (1.1 MB), 6 of them press photos of real players | Remove (copyright) |
| `assets/csv/*` | **Deleted in HEAD** (commits `845b6c5`, `9acc629`, `f817e9a`) | Restore from commit `25cb0ac`, then clean |
| `requirements.txt`, `runtime.txt`, `Procfile` | Heroku-era pins, Python 3.7.11 | Replace with `pyproject.toml` + `uv.lock` + `Dockerfile` |
| Scraper and ML model | **Not in the repository** (`selenium` is pinned, which suggests an odds scraper lived elsewhere) | Needs the owner, see §9 |

### 2.2 Findings

Severity: 🔴 blocks sharing · 🟠 wrong or misleading output · 🟡 quality/maintainability

**Runtime and stack**
- 🔴 The app crashes on import because `assets/csv/*.csv` no longer exists in HEAD.
- 🔴 Python 3.7 and Dash 1.19 are end-of-life. `import dash_core_components` fails on any current Dash, and `DataFrame.append` was removed in pandas 2.0.
- 🔴 `wincertstore` is Windows-only, so `pip install -r requirements.txt` fails on Linux/Docker with current pip.
- 🟡 Heavy unused dependencies (`selenium`, `matplotlib`, `scikit-learn` only used for `accuracy_score`, `scipy`).
- 🟡 All Python code lives in `assets/`. Dash serves that folder publicly as static files, so **the source code is downloadable from the live site** (`/assets/functions_and_datasets.py`). Dash also auto-loads any `.css`/`.js` it finds there.

**Correctness (data and metrics)**
- 🟠 **European game dates are corrupted.** The data was parsed month-first whenever the day was ≤ 12, so 6 Oct 2010 became `2010-06-10`. Every `Season` label derived from those dates is wrong too (~15% of European games fall outside their labelled season). NBA dates are fine. I verified the fix against the original `all_dataset.csv` in history: after swapping, 24,203 of 24,203 European rows match exactly.
- 🟠 The summary table reports "Accuracy Results" for *All Predictions* using the **line** accuracy variable (`[accuracy_result_rec, accuracy_line_all]`).
- 🟠 **Filters don't combine.** On the Data page, picking a league throws away the season filter, and picking a team throws away both. The same happens in the scatter explorer. The UI even says "!! Do Refresh the page after each selection".
- 🟠 **Pushes count as losses.** When the total lands exactly on the line (15 archive games) the old code labels it "Under". It is a push: the stake comes back.
- 🟠 99 games where the predicted total equalled the line are labelled "Under" in the raw archive. They are *no pick* (the old code handled this in one place and not in others).
- 🟠 9 duplicate rows in the prediction archive inflate the counts.
- 🟠 Only accuracy is shown. For betting, accuracy without the odds means nothing: 60% at average odds of 1.40 loses money. **ROI at a flat stake** is the metric that matters, and it's missing.
- 🟡 Outcome labels are Greek betting slang (`Assos`/`Diplo`, meaning 1/2). Visitors won't understand them.

**UI/UX**
- 🔴 Header images are press photos of real athletes. That's a copyright and likeness problem the moment the site is shared.
- 🔴 Tables are `editable=True` and `row_deletable=True`, so visitors can "edit" the model's track record.
- 🟠 The full 35k-row, 25-column dataset is serialised into the page (~8 MB of JSON), plus base64-inlined images on every page. First load is slow.
- 🟡 Three tables share `id='table'` (invalid, and it breaks callbacks).
- 🟡 Layout uses hard-coded pixel offsets (`left: 125px`) and empty `dbc.Col()` spacers, so it breaks on phones. `font-family: cursive`, yellow-on-black buttons.
- 🟡 Dropdowns list every raw column, including internal ones such as `Odd_Home_Skew`.
- 🟡 The upcoming-predictions table shows games from 14 May 2022 as if they were upcoming.

**Operations**
- 🔴 No tests, no CI, no reproducible environment, no Docker image.
- 🟡 The README still mentions Heroku (free tier removed 2022) and links to a Render URL that crashes.
- 🟡 Personal email shown in a modal. Better as an optional config value.

### 2.3 What's worth keeping

- **The data.** 35,326 games (2010-11 → 2020-21) across NBA, EuroLeague, EuroCup, BCL, ACB, Lega A, LNB, BBL, Greek Basket League, Turkish Super Lig and VTB. They include opening/closing odds, odds dispersion, implied probabilities and rolling scoring averages, which is a genuinely rich feature set.
- **The prediction archive.** 1,301 published picks (Sep 2021 → May 2022) with actual results, an honest out-of-sample track record.
- **The concept.** League/team exploration next to model predictions and their track record.

---

## 3. Goals and principles

**What "shareable" means here**

1. Opens in under ~2 s and works on a phone.
2. Every number is correct, defined, and reproducible from the repo.
3. It's honest. Stale data is labelled as stale, ROI is shown next to accuracy, and there is a responsible-gambling notice.
4. A stranger can clone the repo and run it with one command. A reviewer can read the code and find it tidy.
5. Deploys automatically from `main`, and CI stops a broken build from shipping.

**Engineering principles**

- *Pure core, thin UI.* Cleaning and metrics are plain functions over DataFrames with unit tests. Dash callbacks only wire inputs to those functions.
- *Data is an artefact with a contract.* Processed Parquet files have a documented schema, and one script rebuilds them from raw inputs.
- *No computation at import time* except loading the cached processed files.
- *Boring, current tools.* Python 3.13, Dash 4, pandas 3, uv, ruff, pytest, Docker.

**Non-goals (for now)**: user accounts, placing bets, paid tiers, a JS/React rewrite.

---

## 4. Target architecture

### 4.1 Stack decision

| Concern | Choice | Why |
|---|---|---|
| Language | Python 3.13 | The owner's data/ML work is Python, and one language keeps the pipeline and the app together |
| Web framework | **Dash 4** with Dash Pages | Keeps the owner's existing knowledge. It's modern enough (multi-page routing, pattern callbacks), and nothing about the product needs a separate SPA |
| UI kit | dash-bootstrap-components 2 (Bootstrap 5.3) + a custom stylesheet + Bootstrap Icons | Responsive grid, dark theme, accessible components |
| Tables | **dash-ag-grid** | Replaces DataTable, which is effectively in maintenance mode. Server-side (infinite) row model for the 35k-row table |
| Charts | Plotly 7 with one shared custom template | Consistent look across all charts |
| Data | pandas 3 + Parquet (pyarrow) | 35k rows fit easily in memory. Parquet is typed and ~10× smaller than the CSVs |
| Env and deps | uv + `pyproject.toml` + `uv.lock` | Reproducible, fast |
| Quality | ruff (lint + format), pytest | |
| Serving | gunicorn in Docker (`python:3.13-slim`) | Runs the same everywhere |
| Hosting | Render (blueprint in `render.yaml`) | Already the stated host. Free plan works; the Starter plan avoids cold starts |
| CI | GitHub Actions: lint → test → docker build | |

**Alternatives considered.** (a) *FastAPI + React/Next.js*: the nicest possible UI, but it doubles the codebase and moves the owner off Python for the frontend. Reconsider only if the product outgrows Dash (accounts, heavy interactivity). (b) *Streamlit*: fastest to write, but its rerun model and limited layout control make it feel like a notebook rather than a product. Dash 4 sits in between.

### 4.2 Repository layout

```
betting-dashboard/
├── pyproject.toml / uv.lock        # deps, tool config
├── Dockerfile / .dockerignore
├── render.yaml                     # Render blueprint (infra-as-code)
├── .github/workflows/ci.yml
├── README.md                       # pitch, screenshots, quickstart
├── docs/
│   ├── REVIVAL_PLAN.md             # this file
│   └── DATA.md                     # data dictionary and metric definitions
├── data/processed/                 # versioned, small, typed artefacts
│   ├── games.parquet               # historical games (35k)
│   ├── predictions.parquet         # graded prediction archive (1.3k)
│   └── upcoming.parquet            # latest published slate
├── scripts/
│   └── build_data.py               # raw CSV → processed Parquet (reproducible)
├── src/betting_dashboard/
│   ├── app.py                      # create_app() factory + `server` for gunicorn
│   ├── config.py                   # settings from env vars
│   ├── data/
│   │   ├── schema.py               # column names, labels, league metadata
│   │   ├── cleaning.py             # pure raw → clean transforms
│   │   └── store.py                # cached loaders for processed files
│   ├── analytics/
│   │   ├── betting.py              # pick grading, P&L, ROI, summaries
│   │   └── games.py                # filtering, team/league aggregates
│   ├── components/                 # navbar, footer, KPI cards, grid, chart theme
│   ├── pages/                      # overview, predictions, explorer, teams, games, about, 404
│   └── assets/                     # style.css, favicon, logo (static only, no code)
└── tests/                          # unit tests for cleaning/analytics + app smoke tests
```

### 4.3 Runtime data flow

```
             build time                                     run time
┌────────────────────────────┐   ┌──────────────────────────────────────────────────────┐
│ raw CSVs (git history /    │   │ gunicorn → Flask → Dash                              │
│ future scraper output)     │   │   store.py  ──lru_cache──▶ DataFrames (read once)    │
│        │                   │   │        │                                             │
│        ▼                   │   │        ▼                                             │
│ scripts/build_data.py      │   │   analytics/*  (pure functions)                      │
│  └ data/cleaning.py        │   │        │                                             │
│        │                   │   │        ▼                                             │
│        ▼                   │   │   pages/* callbacks ──▶ Plotly figures / AG Grid rows │
│ data/processed/*.parquet ──┼──▶│                                                      │
└────────────────────────────┘   └──────────────────────────────────────────────────────┘
```

When the pipeline returns (Phase 4), a scheduled job writes new Parquet files, and the app picks them up on the next deploy (or through a file-mtime cache check if the files move to object storage).

---

## 5. Product and UI redesign

### 5.1 Information architecture

| Route | Page | Replaces | Purpose |
|---|---|---|---|
| `/` | **Overview** | – | Track record, opening on the **recommended strategy** (totals, edge > 2.5): a comparison strip (recommended vs all picks), KPI cards (picks, hit rate vs break-even, units, ROI), cumulative profit, ROI by competition, and an edge slider plus an edge-threshold chart that shows why 2.5 |
| `/predictions` | **Predictions** | Predictions | Latest slate (labelled with its date, plus a "paused" banner while stale) and the full graded archive with win/loss/push highlighting and filters |
| `/explorer` | **League explorer** | Home (left) | Scatter of any two *meaningful* features with filters that actually combine, colour by league/outcome, plus scoring-trend and home-advantage charts |
| `/teams` | **Teams** | Home (right) | Pick a team: record, points for/against by season, home/away split, over/under record against the line, recent games |
| `/games` | **Game data** | Data | The full historical table, server-side sort/filter/paging, CSV export of the current filter |
| `/about` | **About** | Footer | Methodology, metric definitions, data coverage, disclaimer, contact links |

### 5.2 Design system

- **Theme:** dark, "sports analytics" look. Near-black navy background (`#0b1220`), elevated surface cards (`#111a2e`), one accent (basketball orange `#f59e0b`), plus semantic green/red for win/loss and grey for push.
- **Type:** Inter, self-hosted along with Bootstrap and its icons so the site makes no third-party requests. Tabular numerals for all figures.
- **Layout:** Bootstrap grid, max-width container, cards with 12–16 px radius. It collapses to one column on phones, and the navbar collapses into a hamburger menu.
- **Charts:** one registered Plotly template (transparent background, muted grid, Inter font, the accent-led palette), so every chart looks the same.
- **Copy:** plain English labels ("Home win" rather than `Assos`, "Total points line" rather than `Line`), with a units note on every KPI.
- **Branding:** a text-and-icon logo. No third-party imagery. The working name is set in one config value (`APP_NAME`).

### 5.3 Accessibility and performance targets

- Colour contrast ≥ 4.5:1 for text. Win/loss is never shown by colour alone (there's also an icon/label).
- Initial HTML+JSON payload < 500 KB on any page. Large tables load rows on demand.
- Lighthouse performance ≥ 85 and accessibility ≥ 90 on the Overview page.

---

## 6. Data and analytics

### 6.1 Cleaning rules (implemented in `data/cleaning.py`, documented in `docs/DATA.md`)

1. **Date repair (European leagues).** If the stored day ≤ 12, swap day and month. NBA rows are left alone. Verified 100% against the original day-first source file.
2. **Season** is recomputed from the repaired date: a season starts on 1 August.
3. **Outcomes** get plain labels: `home`/`away` winner, `over`/`under`/`push` against the line.
4. **Archive:** exact duplicates are dropped. Totals picks where predicted total == line become *no pick*. Every pick is graded as win/loss/push.
5. The only columns kept are the ones the app uses, with explicit dtypes (categoricals for league/team).

### 6.2 Metric definitions

| Metric | Definition |
|---|---|
| **Pick** | Totals: over/under vs the line. Moneyline: the side the model predicts to win |
| **Hit rate** | wins ÷ (wins + losses). Pushes are excluded |
| **Units** | Profit at 1-unit flat stake: win → `odds − 1`, loss → `−1`, push → `0` |
| **ROI** | units ÷ stakes (pushes count as stakes returned, so they're excluded from the denominator) |
| **Odds used** | Moneyline: the market *mean* odds for the picked side, as recorded. Totals: the archive doesn't store over/under prices for the prediction window, so a standard **1.90** is assumed and labelled as such (break-even hit rate 52.6%) |
| **Edge** | \|predicted total − line\|. The old "recommended" picks are edge > 2.5, which is now an adjustable slider |

### 6.3 Findings from the cleaned archive

These are shown in the UI, not hidden. Being upfront about them is what makes the site credible to share.

| Slice | Picks | Hit rate | Units | ROI |
|---|---|---|---|---|
| Totals, all picks | 1,193 (595-584-14) | 50.5% (break-even 52.6%) | −48.5u | −4.1% |
| Totals, edge > 2.5 (legacy "recommended") | 180 (97-81-2) | 54.5% | +6.3u | **+3.5%** |
| Moneyline, all picks | 1,292 | 67.6% (break-even 69.9%) | −89.5u | −6.9% |

- The model leaned heavily toward *Under* (758 vs 435 totals picks).
- The one profitable slice, high-edge totals, is a small sample (180 picks). It's a hypothesis to test in Phase 6, not proof of an edge.
- By competition, the Bundesliga, Turkish Super League, VTB and LKL were positive, while the Greek Basket League, ABA and Lega A were clearly negative.

---

## 7. Deployment and operations

| Item | Plan |
|---|---|
| Container | Multi-stage `Dockerfile`: uv installs locked deps into a venv, the slim runtime image runs as a non-root user, and gunicorn serves `betting_dashboard.app:server` on `$PORT`. The image is about 800 MB unpacked, mostly pyarrow/pandas/plotly. Slimming it is a backlog item |
| Hosting | `render.yaml` blueprint: Docker web service, health check on `/healthz`, auto-deploy from `main`. The free plan is fine for sharing (cold start ~30 s); the Starter plan removes cold starts |
| Config | Env vars only: `APP_NAME`, `CONTACT_EMAIL`, `GITHUB_URL`, `DATA_DIR`, `LOG_LEVEL`. `.env.example` documents them |
| CI | GitHub Actions on push/PR: `uv sync --locked` → `ruff check` → `ruff format --check` → `pytest` → `docker build`. The build must be green to merge |
| Caching | Processed frames are loaded once per worker (`lru_cache`). Figures are cheap, so they aren't cached |
| Observability | Structured logs to stdout (Render collects them) and the `/healthz` endpoint. Optional in Phase 5: Sentry, privacy-friendly analytics (Plausible/Umami) |
| Custom domain | Optional. Render supports it with automatic TLS |

**Rollout.** Merge this branch → create the Render service from the blueprint (one click) → point the README badge and link at it → retire the old Render service.

---

## 8. Roadmap

| Phase | Scope | Acceptance criteria | Status |
|---|---|---|---|
| **0. Rescue** | Restore data from git history, audit it, write this plan | Data recovered, findings documented | ✅ Done |
| **1. Foundation** | Package layout, pyproject/uv, cleaning + analytics modules with tests, Parquet artefacts, build script | `uv run pytest` green, `scripts/build_data.py` reproduces `data/processed/` byte-for-byte | ✅ Done |
| **2. UI rebuild** | Six pages from §5, design system, responsive layout, no third-party images | Every page renders with no console errors and has no horizontal overflow at phone width (checked at 390 px) | ✅ Done |
| **3. Ship** | Dockerfile, render.yaml, CI workflow, README, DATA.md | `docker build` + container smoke test pass, CI green | ✅ Done: image built and smoke-tested locally. CI runs on the first push/PR. Creating the Render service needs the owner's account |
| **4. Live pipeline** | Ingestion for fixtures/odds/results, retrained model, scheduled refresh | New predictions appear daily without manual steps. Archive auto-grades | ⏸ Deferred: the owner chose a showcase first. Restart from the original code if it turns up (§9) |
| **5. Portfolio polish** | Social preview image and author/contact links (done). Next: see §8.1 | – | In progress |
| **6. Model lab** | Proper backtest harness, calibration plots, closing-line value (CLV) tracking, per-league models | Published backtest report in the app | Backlog |

### 8.1 Portfolio enhancements, in suggested order

1. **Model lab page (the biggest win).** The original model code is lost, so retrain a transparent model on the 35k-game dataset with walk-forward validation. Publish a backtest, calibration plot and feature importance on a new page. This shows the ML work itself, which recruiters care about most, and it also produces the Phase 4 model if live picks ever return.
2. **"How this was built" case study.** Tell the rescue story on a page or in a blog post on the portfolio site: deleted data recovered from git, the date-swap bug, pushes graded as losses, and why ROI beats accuracy. Debugging and judgement stories read well to hiring managers.
3. **Keep-alive ping.** Render's free tier sleeps after 15 minutes idle, so a recruiter's first visit waits about 30 seconds. A GitHub Actions cron that hits `/healthz` every 10 minutes during European and US working hours avoids that and stays within the free instance hours.
4. **Link it everywhere.** Add a project card with the social preview image to the portfolio site, a featured link on LinkedIn, and a short demo GIF in the README.
5. **Privacy-friendly visitor stats** (e.g. GoatCounter, free, no cookies) to see whether the links get clicked.
6. **Accessibility/performance audit** against the §5.3 targets, plus an optional light theme.

---

## 9. Phase 4: bringing the prediction pipeline back

The repo contains the *outputs* of a pipeline (feature-rich game rows and prediction files named `next_daysNN.csv`) but not the pipeline itself. Reviving it has three parts:

**9.1 Ingestion (fixtures, odds, results)**
- *Option A (recommended): a licensed odds API* (e.g. The Odds API, which covers EuroLeague, NBA and several European domestic leagues; paid tiers are cheap at this volume). Stable and legal, with no scraper maintenance.
- *Option B: revive the Selenium scraper* (probably OddsPortal-style, judging by the odds-dispersion features). It's free, but brittle, likely against the site's ToS, and it breaks whenever the site changes.
- Results can come from the same API, or from a free stats source per league.

**9.2 Model**
- Rebuild feature engineering from the existing columns (rolling team scoring, market-implied probabilities, odds movement first→last).
- Train one gradient-boosted regressor per target (home and away points) on 2010–2021, then add 2021 onward as it's ingested. Validate with **walk-forward (time-series) splits**, never random splits.
- Track **closing-line value** as well as P&L. It's the fastest honest signal of whether a betting model has real edge.

**9.3 Orchestration**
- A scheduled GitHub Actions workflow (daily, e.g. 06:00 Europe/Athens) runs `ingest → grade yesterday's picks → predict today's slate → write Parquet`, then commits the data or uploads it to object storage (Cloudflare R2 or S3).
- The app reads `upcoming.parquet`. The "paused" banner disappears on its own once the slate date is current, because the banner is driven by data freshness rather than a flag.
- Secrets (API keys) live in GitHub Actions secrets, never in the repo.

**9.4 Data contract** (already enforced by the app and tests). New pipeline outputs must match the schemas in `data/schema.py`. The build script validates them and fails loudly on drift.

---

## 10. Risks, legal and responsible-gambling notes

| Risk | Mitigation |
|---|---|
| Copyrighted player photos | Removed. Only original, generated or licensed imagery from now on |
| Being read as financial/betting advice | A persistent disclaimer in the footer and About page ("for research and entertainment; no guarantee; 18+; gamble responsibly"), with links to support services such as BeGambleAware and the Greek KETHEA helpline |
| Scraping terms of service | Prefer a licensed API (§9.1) |
| Data redistribution | The historical odds were presumably scraped. Confirm before publishing the raw dataset for download; the app currently exposes filtered views and CSV export (can be switched off with a config flag if needed) |
| Free-tier cold starts | Acceptable for a portfolio. Upgrade the plan if it's shared widely |
| Owner's personal data | Email is optional config and off by default. The personal photo is removed |

---

## 11. Owner decisions and open questions

**Answered (2026-09-27)**

| # | Question | Answer |
|---|---|---|
| 1 | Is the scraper/model code still around? | Not to hand; the owner may find it. If it turns up, Phase 4 starts from it (§9) instead of a rebuild |
| 2 | Live predictions or showcase? | **Showcase** for now. Phase 4 is deferred |
| 3 | Name | **Courtside Analytics** |
| 4 | Include NBA picks in the record? | **Yes**, every league is included |
| 5 | Licence | **MIT** for the code (`LICENSE`) |
| 6 | Audience | **Portfolio / showcase** |
| 7 | Hosting | **Render free tier** (cold starts accepted) |
| 8 | Contact | **Email, GitHub, LinkedIn and portfolio site**, in the footer and on an "About the author" card. Each is a config value, and setting one to empty hides it |
| 9 | Default view | **The recommended strategy** (totals picks with edge > 2.5) is what the Overview and the Predictions track record open on. The full record is one click away and always shown alongside |

No questions are open right now.

---

## 12. Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-27 | Stay on Python/Dash (upgrade to Dash 4) rather than a React rewrite | The owner's skill set, and it keeps one language shared with the future ML pipeline |
| 2026-09-27 | Parquet artefacts are committed to the repo (~1 MB) | Small, reproducible, no external storage needed until Phase 4 |
| 2026-09-27 | ROI at flat stake is the headline metric, with totals odds assumed at 1.90 | Accuracy alone is misleading for betting. The archive has no totals prices |
| 2026-09-27 | Pushes are graded as pushes, and predicted total == line counts as no pick | Correct betting semantics |
| 2026-09-27 | Removed all third-party player photos | Copyright/likeness |
| 2026-09-27 | dash-ag-grid replaces DataTable | Better UX, server-side row model, active development |
| 2026-09-27 | Bootstrap, Bootstrap Icons and Inter are vendored under `assets/vendor` | No third-party requests (privacy, speed, works behind strict networks) |
| 2026-09-27 | Overview and the Predictions track record open on the recommended strategy (edge > 2.5), with the all-picks figures always shown next to it | Owner request. It is the strategy the original site published. Showing the full record alongside keeps it honest |
| 2026-09-27 | MIT licence; name "Courtside Analytics" | Owner decisions |
| 2026-09-27 | Contact links (email, GitHub, LinkedIn, portfolio) in the footer and About page; social preview image on every page; ProxyFix so preview URLs are https behind Render | Owner request; links shared on LinkedIn get a proper preview card |
