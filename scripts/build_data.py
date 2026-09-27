"""Rebuild data/processed/*.parquet from the raw inputs in data/raw/.

    uv run python scripts/build_data.py

The raw files are the legacy CSVs recovered from git history (commit 25cb0ac), stored
gzipped and unmodified. The output is deterministic, so re-running it on unchanged inputs
produces no git diff.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from betting_dashboard.data.cleaning import clean_archive, clean_games, clean_upcoming

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

SOURCES = {
    "games": ("nba_plus_europe.csv.gz", clean_games),
    "predictions": ("all_archive.csv.gz", clean_archive),
    "upcoming": ("next_days89.csv.gz", clean_upcoming),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (filename, clean) in SOURCES.items():
        raw = pd.read_csv(RAW / filename, index_col=0)
        df = clean(raw)
        path = OUT / f"{name}.parquet"
        df.to_parquet(path, index=False, compression="zstd")
        print(f"{name:<12} {len(raw):>6} raw rows -> {len(df):>6} rows  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
