# Data dictionary

The app reads three Parquet files from `data/processed/`. `scripts/build_data.py` rebuilds them deterministically from the raw CSVs in `data/raw/`. The column contracts live in `src/betting_dashboard/data/schema.py`. Both the build and the app validate files against them, so if a future pipeline produces anything different, it fails loudly.

## Sources

| Raw file | Origin | Rows |
|---|---|---|
| `nba_plus_europe.csv.gz` | Legacy historical dataset, recovered from git commit `25cb0ac` | 35,326 |
| `all_archive.csv.gz` | Legacy archive of published predictions with final scores | 1,301 |
| `next_days89.csv.gz` | The last prediction slate the old pipeline published (14–15 May 2022) | 16 |

The raw files are stored gzipped and otherwise byte-identical to the originals.

## Cleaning rules

1. **European dates are repaired.** The source wrote dates as `dd/mm/yyyy`, and a later step parsed them month-first wherever it could (day ≤ 12), so 6 Oct 2010 was stored as `2010-06-10`. For non-NBA rows, any stored date whose day is ≤ 12 has its day and month swapped back. This was checked against the original day-first file in git history (`all_dataset.csv`, commit `bb78e47`): after repair, all 24,203 European rows match. NBA dates were already correct and are left alone.
2. **Seasons are recomputed** from the repaired date. A season runs from 1 August to 31 July and is labelled like `2019-20`. The stored `Season` column was derived from the broken dates, so it is discarded.
3. **League codes get display names** (`Champions-League` becomes `Basketball Champions League`, and so on).
4. **Outcomes use plain labels.** `winner` is `home`/`away`. `total_result` is `over`/`under`/`push` against the line.
5. **Prediction archive:**
   - Exact duplicate rows are dropped (9 rows).
   - `Assos`/`Diplo` (Greek slang for 1/2) become `ml_pick = home/away`.
   - `total_pick` is derived from the predicted total vs the line. When they are equal it is left empty (no pick). The raw file labelled these 99 rows "Under".
   - `edge` = |predicted total − line|. It equals the raw `Difference` column.

## `games.parquet`

| Column | Meaning |
|---|---|
| `date`, `tip_off`, `season` | Game date, local tip-off time (HH:MM), season label |
| `league`, `home_team`, `away_team` | Competition and teams |
| `home_score`, `away_score`, `total_points`, `margin` | Final score, sum, and home margin |
| `winner` | `home` or `away` |
| `line`, `total_result` | Bookmaker total-points line, and `over`/`under`/`push` |
| `odd_over`, `odd_under` | Totals prices |
| `odd_home`, `odd_away` | Mean moneyline price across bookmakers |
| `odd_*_open`, `odd_*_close` | First and last recorded moneyline price |
| `home_implied_prob`, `away_implied_prob` | 1 ÷ mean price (includes the bookmaker margin, so the pair sums to more than 1) |
| `home_avg_points`, `away_avg_points` | Team scoring average before the game |
| `home_avg_points_at_home`, `away_avg_points_away` | The same, split by venue |

## `predictions.parquet` / `upcoming.parquet`

| Column | Meaning |
|---|---|
| `date`, `tip_off`, `league`, `home_team`, `away_team` | Game |
| `odd_home`, `odd_away` | Mean moneyline price when the prediction was published |
| `pred_home_score`, `pred_away_score`, `pred_total` | Model output |
| `line`, `edge` | Totals line and \|pred_total − line\| |
| `ml_pick`, `total_pick` | `home`/`away` and `over`/`under`/empty |
| `home_score`, `away_score` | Final score (archive only) |

When loaded, `analytics.betting.grade_predictions` adds `ml_odds`, `ml_result`, `ml_units`, `total_odds`, `total_result` and `total_units`.

## Metric definitions

| Metric | Definition |
|---|---|
| Hit rate | wins ÷ (wins + losses). Pushes are excluded |
| Units | Profit at a flat 1-unit stake: win → `odds − 1`, loss → `−1`, push → `0` |
| ROI | units ÷ decided picks |
| Break-even | 1 ÷ average odds |
| Totals price | The archive has no over/under prices for the prediction window, so **1.90** is assumed (break-even 52.6%) |
| Moneyline price | The recorded market mean for the picked side |
