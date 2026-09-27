# Backlog

Portfolio enhancements for Courtside Analytics, in suggested order. Each task is self-contained: a description a person can follow, and a **prompt** you can paste into a fresh Claude Code session on this repository.

Status key: ⬜ not started · 🟨 in progress · ✅ done

| # | Task | Status | Size | Needs from the owner |
|---|---|---|---|---|
| 1 | [Model lab page](#1-model-lab-page) | ⬜ | L (2–3 sessions) | Nothing |
| 2 | ["How this was built" case study](#2-how-this-was-built-case-study) | ⬜ | M | Review the draft; add it to the portfolio site |
| 3 | [Keep-alive ping for the free tier](#3-keep-alive-ping-for-the-free-tier) | ⬜ | S | The live URL, set as a repository variable |
| 4 | [Link it everywhere (demo GIF, live link, promo copy)](#4-link-it-everywhere) | ⬜ | M | The live URL; post on LinkedIn; update the portfolio site |
| 5 | [Privacy-friendly visitor stats](#5-privacy-friendly-visitor-stats) | ⬜ | S | A free GoatCounter account (site code) |

---

## Before you start (for any session)

Read these first. They are the house rules that every task below assumes.

- **Docs:** `README.md`, `docs/REVIVAL_PLAN.md` (architecture, decisions, §8.1), `docs/DATA.md` (schemas, cleaning rules, metric definitions).
- **Commands:** `uv sync` · `uv run pytest` · `uv run ruff check . && uv run ruff format --check .` · `uv run python scripts/build_data.py` (must leave `data/processed/` unchanged) · `uv run python -m betting_dashboard.app` (serves on :8050).
- **Layout:** pure logic goes in `src/betting_dashboard/analytics/` (with unit tests). Pages in `src/betting_dashboard/pages/` expose `PATH, NAME, TITLE, DESCRIPTION, layout()` and are registered in `pages/__init__.py` (`PAGES`) and `app.py`. Shared UI goes in `components/` (`card`, `kpi`, `graph`, `field`, `dropdown`, `data_grid`, the Plotly template in `theme.py`).
- **Hard constraints:**
  - **512 MB RAM** on Render's free plan. One gunicorn worker with the data loaded uses about 250 MB. Don't add heavy runtime dependencies or train models at request time. Precompute offline into `data/processed/`.
  - **No third-party requests by default.** CSS, fonts and icons are vendored, and a test enforces this for the index page. Anything external must be opt-in via config.
  - **Honest numbers.** The Overview opens on the recommended strategy (totals, edge > 2.5), always shown next to the full record. Never present a figure without its sample size and baseline.
  - The site is a **showcase**. Live predictions are deferred (Phase 4 in the plan).
- **Definition of done:** tests and lint pass, the data rebuild shows no diff, every page loads in a browser with no console errors at 1440 px and 390 px, the docs are updated (plan decision log plus this file's status), and a PR is opened against `main`.

---

## 1. Model lab page

**Why.** The original model's code is lost, so the site shows *results* but not the *machine-learning work*. For a portfolio, the modelling is the most valuable thing to show. A transparent, reproducible model trained on the 35k-game dataset fills that gap. It also becomes the starting point if live predictions ever return.

**What to build**

1. **Offline training script** `scripts/train_model.py`, using a separate dependency group (`uv add --group model scikit-learn`) so the Docker image and its 512 MB budget stay the same.
   - Inputs: `data/processed/games.parquet`.
   - **Leakage check first.** Confirm that `home_avg_points`, `away_avg_points`, `home_avg_points_at_home` and `away_avg_points_away` are *pre-game* values. Recompute rolling averages from past scores for a few teams and compare. If they include the current game, rebuild them from scores with a strict shift. Document the finding in `docs/DATA.md`.
   - Targets: (a) `total_points` (regression), from which over/under picks are made against `line`; (b) home win (classification).
   - Features: only pre-game columns. That means the line, over/under and moneyline prices (mean, open, close), implied probabilities, pre-game scoring averages, league (one-hot), and month of season. No scores or results.
   - Validation: **walk-forward by season**. For each season S from 2013-14 onward, train on all earlier seasons and predict S. Never use random splits.
   - Model: `HistGradientBoostingRegressor` / `Classifier`, plus a baseline (the line itself for totals, and de-vigged market probability for the winner).
   - Outputs written to `data/processed/`: `model_backtest.parquet` (one row per test game: season, league, prediction, pick, edge, actual, graded result using the **real** `odd_over`/`odd_under` prices), `model_calibration.parquet` (probability bins, predicted vs observed, model vs market), `model_importance.parquet` (permutation importance on the latest fold), and `model_meta.json` (training date, folds, metrics).
2. **Analytics** in `analytics/model.py`: helpers that read those files and summarise ROI by edge threshold, ROI by season, calibration and Brier score (model vs market), with unit tests.
3. **Page** `/model` ("Model lab"), placed between Teams and Game data in `PAGES`:
   - KPI row: backtest picks, hit rate vs break-even, ROI, and Brier score of model vs market.
   - Charts: ROI by edge threshold (compare with the Overview's "Why 2.5 points?"), ROI by season (is it stable?), a calibration plot (model and market against the diagonal), and feature importance.
   - A plain-English methodology box: walk-forward, no leakage, real prices, and what "beating the market" would require.
   - Honest framing. If the model doesn't beat the market, say so. That is still a strong portfolio result when it is explained well.
4. **Tests:** fold boundaries (every training date is before every test date), grading with real prices, page layout serialisation, and a smoke test for the callbacks.
5. **CI:** do *not* retrain in CI. Commit the artefacts and add a check that `model_meta.json` matches the schema.

**Acceptance criteria**
- `uv run python scripts/train_model.py` reproduces the committed artefacts (fixed random seeds).
- `/model` renders with no console errors, and gunicorn worker memory stays under 300 MB.
- The docs are updated: DATA.md (new files, leakage finding) and the REVIVAL_PLAN decision log.

**Prompt for Claude**

> Read `docs/BACKLOG.md` (the "Before you start" section and task 1), `docs/REVIVAL_PLAN.md` and `docs/DATA.md`. Build the Model lab exactly as task 1 describes. Start with the leakage check on the pre-game scoring averages and report what you find before modelling. Keep scikit-learn out of the runtime image (use a `model` dependency group), train offline with walk-forward validation by season, write the artefacts to `data/processed/`, add `analytics/model.py` with tests, and add a `/model` page that matches the existing design system. Grade totals picks with the real `odd_over`/`odd_under` prices. Present results honestly against the market baseline. Verify in a real browser at 1440 px and 390 px, check worker memory, update the docs, then open a PR against `main`.

---

## 2. "How this was built" case study

**Why.** Hiring managers respond to stories about judgement: what was broken, how you found it, what you decided and why. This project has several good ones, and they're currently buried in commit messages and the plan.

**What to build**
1. `docs/CASE_STUDY.md` (roughly 1,200–1,800 words, with images). Suggested structure:
   1. **The starting point:** a parked 2021 Dash app that couldn't start, because its data had been deleted from the repo.
   2. **Rescue:** recovering the datasets from git history (`git show 25cb0ac:…`), and making the processed data reproducible byte-for-byte.
   3. **The date bug:** European dates had been parsed month-first when the day was ≤ 12, which also corrupted the season labels. Explain how it was detected (games outside their season) and verified (24,203/24,203 rows match the original day-first file). Include a small before/after chart.
   4. **Grading that tells the truth:** pushes, "no pick" rows, duplicates, and why **ROI beats accuracy** (67.6% moneyline hit rate still loses money at average odds of 1.43).
   5. **The recommended strategy:** edge > 2.5 → +3.5% ROI on 180 picks vs −4.1% overall, with the caveats (small sample, assumed 1.90 totals price).
   6. **Engineering:** package layout, tests, server-side grid, vendored assets, Docker, fitting 512 MB, CI.
   7. **What I'd do next:** link to the Model lab, or to the backlog if it isn't built yet.
2. Optional in-app version: a `/story` page that renders the markdown with `dcc.Markdown` (linked from About, not from the main nav).
3. A shorter (~600 words) version for the portfolio site at `docs/CASE_STUDY_SHORT.md`, ready to paste.

**Acceptance criteria:** every number in the text is produced by code (add a small `scripts/case_study_numbers.py` that prints them), the images live in `docs/images/`, and the owner reviews the text before it's published.

**Prompt for Claude**

> Read `docs/BACKLOG.md` (task 2), `docs/REVIVAL_PLAN.md`, `docs/DATA.md` and the git history (`git log --stat`). Write `docs/CASE_STUDY.md` following the structure in task 2, plus a ~600-word `docs/CASE_STUDY_SHORT.md` for the owner's portfolio site. Write in the first person as the owner (Konstantinos Sakellariou), in plain, specific language. Generate every figure you quote with a new `scripts/case_study_numbers.py`, and create a before/after chart of the date repair in `docs/images/`. Don't invent facts about the original model. If something is unknown, say so. Optionally add a `/story` page linked from About. Open a PR and ask the owner to review the wording.

---

## 3. Keep-alive ping for the free tier

**Why.** Render's free web services spin down after about 15 minutes without traffic. The next visitor then waits roughly 30–60 seconds for a cold start, which is a bad first impression when a recruiter clicks the link.

**What to build**
- `.github/workflows/keepalive.yml`:
  - `on: schedule` with cron `*/10 6-21 * * *` (every 10 minutes, 06:00–21:59 UTC, which covers European and US working hours), plus `workflow_dispatch` for manual runs.
  - One step: `curl --fail --silent --show-error --max-time 90 --retry 2 "${{ vars.SITE_URL }}/healthz"`. Skip cleanly with a notice if `vars.SITE_URL` isn't set.
  - `permissions: {}` (it needs nothing).
- README: a short "Keep-alive" note under Deployment.

**Things to know**
- The free plan includes a monthly allowance of instance hours per workspace (enough for one service running all month). Pinging only during working hours stays well within it, even if the owner has another free service. Check Render's current free-tier page before relying on exact numbers.
- GitHub may delay scheduled runs and **disables scheduled workflows after 60 days without repository activity**. Re-enable it from the Actions tab if that happens.

**Owner action:** GitHub repo → Settings → Secrets and variables → Actions → **Variables** → New variable `SITE_URL` = the Render URL (no trailing slash).

**Acceptance criteria:** a manual `workflow_dispatch` run succeeds against the live site, and the workflow is a no-op (success with a notice) when `SITE_URL` is missing.

**Prompt for Claude**

> Read `docs/BACKLOG.md` task 3. Add `.github/workflows/keepalive.yml`: it pings `${{ vars.SITE_URL }}/healthz` every 10 minutes between 06:00 and 21:59 UTC and on `workflow_dispatch`, with `permissions: {}`, a 90-second timeout, 2 retries, and a clean skip when the variable is unset. Document it in the README's Deployment section, including the 60-day inactivity caveat. Validate the YAML (e.g. with `actionlint` if available). Open a PR and remind the owner to set the `SITE_URL` repository variable.

---

## 4. Link it everywhere

**Why.** A great project nobody sees doesn't help. The social preview card already exists (`assets/og-image.png`). What's missing is a live link, a moving demo, and copy the owner can post.

**What to build**
1. **Live link:** a "Live demo" badge/link at the top of `README.md`, pointing at `SITE_URL`.
2. **Demo GIF:** `docs/demo.gif` (≤ 5 MB, about 20–30 s, 1280×720). Record it with Playwright's video recording against a local server. Path: the Overview (move the edge slider from 2.5 to 0 and back), Predictions (toggle recommended), the Explorer (filter to EuroLeague), then a team page. Convert to GIF with ffmpeg using a palette (`palettegen`/`paletteuse`, 12–15 fps). Put the recording script in `scripts/record_demo.py` so it can be re-run. Embed the GIF at the top of the README.
3. **Promo copy** in `docs/PROMO.md`:
   - A LinkedIn post (under 1,300 characters), with a hook built on the honest-grading angle, three bullet takeaways, and the link.
   - A LinkedIn "Featured" item title and description.
   - A portfolio-site project card: title, 2-sentence blurb, tech tags, and links (live, code, case study), plus an HTML/Markdown snippet matching a typical GitHub Pages portfolio.
4. **Portfolio site** (optional, separate repo `Konstantinos-Sakellariou/konstantinos-sakellariou.github.io`): if the owner adds it to the session, insert the project card using that site's existing structure.

**Owner actions:** give the live URL; post on LinkedIn and add it to Featured; approve the portfolio-site change.

**Acceptance criteria:** the GIF renders on GitHub and is ≤ 5 MB, the README shows the live link above the fold, and the promo copy is reviewed by the owner.

**Prompt for Claude**

> Read `docs/BACKLOG.md` task 4. The live URL is `<paste URL>`. Add a live-demo link at the top of the README. Write `scripts/record_demo.py`, which uses Playwright video against a local server to record the path in task 4, and convert the result to `docs/demo.gif` with ffmpeg palette generation (≤ 5 MB). Embed it in the README. Write `docs/PROMO.md` with a LinkedIn post, a Featured item and a portfolio project card. If the portfolio repo `Konstantinos-Sakellariou/konstantinos-sakellariou.github.io` is available in this session, add the card there in a separate PR, following that site's structure. Open a PR here first.

---

## 5. Privacy-friendly visitor stats

**Why.** Once the link is shared, it's useful to know whether anyone visits and which pages they look at. GoatCounter is free for personal use, sets no cookies and collects no personal data, so it needs no cookie banner.

**What to build**
- Config: `GOATCOUNTER_CODE` (for example `courtside`, giving `https://courtside.goatcounter.com`). When it's **unset, nothing changes**. The existing test that the index makes no third-party requests must keep passing.
- When it's set:
  - Inject `<script data-goatcounter="https://{code}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>` into `INDEX_TEMPLATE` in `app.py`. Set `data-goatcounter-settings='{"no_onload": true}'` so the page views are counted manually.
  - Dash Pages navigates client-side, so add a **clientside callback** on the pages location (`dash.page_container` includes `dcc.Location(id="_pages_location")`) that calls `window.goatcounter.count({path: pathname})` on every route change, including the first load.
- About page: a one-line privacy note that appears only when analytics is enabled ("Anonymous, cookie-free visit counts via GoatCounter").
- `.env.example` and `render.yaml` (commented example) document the variable.
- Tests: the script is absent when unset and present when set (use `monkeypatch` plus a fresh settings/app instance, or test the template-building function directly).

**Owner action:** sign up at goatcounter.com, choose a site code, then add `GOATCOUNTER_CODE` in the Render service's Environment settings.

**Acceptance criteria:** with the code set, navigating between three pages in a browser records three page views (check GoatCounter's dashboard or the network tab). With it unset, the page makes no requests to goatcounter.com or gc.zgo.at.

**Prompt for Claude**

> Read `docs/BACKLOG.md` task 5 and the "no third-party requests" rule. Add opt-in GoatCounter analytics behind a `GOATCOUNTER_CODE` setting in `config.py`: inject the script into the index template only when it's set, count page views on client-side navigation with a clientside callback on `_pages_location.pathname` (use `no_onload` to avoid double counting), and show a privacy note on the About page when enabled. Add tests for both the set and unset cases, update `.env.example`, the README and the plan's decision log, verify in a browser with the network tab, and open a PR.
