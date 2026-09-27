"""Server-side sort/filter/slice for AG Grid's infinite row model.

The grid sends ``{startRow, endRow, sortModel, filterModel}``; we answer with the requested
slice and the total row count. Supports AG Grid's text, number and date filters, including
two-condition (AND/OR) filters, plus a virtual ``team`` column that matches either side.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

TEAM_COLUMN = "team"

_TEXT_OPS = {
    "contains": lambda s, v: s.str.contains(v, case=False, regex=False),
    "notContains": lambda s, v: ~s.str.contains(v, case=False, regex=False),
    "equals": lambda s, v: s.str.lower() == v.lower(),
    "notEqual": lambda s, v: s.str.lower() != v.lower(),
    "startsWith": lambda s, v: s.str.lower().str.startswith(v.lower()),
    "endsWith": lambda s, v: s.str.lower().str.endswith(v.lower()),
}

_CMP_OPS = {
    "equals": lambda s, a, b: s == a,
    "notEqual": lambda s, a, b: s != a,
    "greaterThan": lambda s, a, b: s > a,
    "greaterThanOrEqual": lambda s, a, b: s >= a,
    "lessThan": lambda s, a, b: s < a,
    "lessThanOrEqual": lambda s, a, b: s <= a,
    "inRange": lambda s, a, b: s.between(a, b),
}


def _condition_mask(series: pd.Series, cond: dict[str, Any]) -> pd.Series:
    kind = cond.get("filterType", "text")
    op = cond.get("type", "contains")
    if op == "blank":
        return series.isna()
    if op == "notBlank":
        return series.notna()

    if kind == "text":
        value = cond.get("filter")
        if value in (None, "") or op not in _TEXT_OPS:
            return pd.Series(True, index=series.index)
        return _TEXT_OPS[op](series.astype("str").fillna(""), str(value)).fillna(False)

    if kind == "number":
        a, b = cond.get("filter"), cond.get("filterTo")
    elif kind == "date":
        a, b = pd.to_datetime(cond.get("dateFrom")), pd.to_datetime(cond.get("dateTo"))
    else:
        return pd.Series(True, index=series.index)
    if a is None or pd.isna(a) or op not in _CMP_OPS:
        return pd.Series(True, index=series.index)
    return _CMP_OPS[op](series, a, b).fillna(False)


def _column_mask(df: pd.DataFrame, column: str, model: dict[str, Any]) -> pd.Series:
    if column == TEAM_COLUMN:
        return _column_mask(df, "home_team", model) | _column_mask(df, "away_team", model)
    if column not in df.columns:
        return pd.Series(True, index=df.index)

    conditions = model.get("conditions")
    if not conditions:
        return _condition_mask(df[column], model)
    masks = [
        _condition_mask(df[column], {"filterType": model.get("filterType"), **c})
        for c in conditions
    ]
    combined = masks[0]
    for mask in masks[1:]:
        combined = combined | mask if model.get("operator") == "OR" else combined & mask
    return combined


def apply_filter_model(df: pd.DataFrame, filter_model: dict[str, Any] | None) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for column, model in (filter_model or {}).items():
        mask &= _column_mask(df, column, model)
    return df[mask]


def apply_sort_model(df: pd.DataFrame, sort_model: list[dict[str, str]] | None) -> pd.DataFrame:
    sort_model = [s for s in (sort_model or []) if s.get("colId") in df.columns]
    if not sort_model:
        return df
    return df.sort_values(
        [s["colId"] for s in sort_model],
        ascending=[s.get("sort") != "desc" for s in sort_model],
        kind="stable",
    )


def rows_for_request(df: pd.DataFrame, request: dict[str, Any]) -> dict[str, Any]:
    """Build a ``getRowsResponse`` for an AG Grid ``getRowsRequest``."""
    filtered = apply_filter_model(df, request.get("filterModel"))
    ordered = apply_sort_model(filtered, request.get("sortModel"))
    start, end = int(request.get("startRow", 0)), int(request.get("endRow", 100))
    page = ordered.iloc[start:end]
    return {"rowData": to_records(page), "rowCount": len(ordered)}


def to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """JSON-safe records: ISO dates, None for missing values."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d")
    return out.astype(object).where(out.notna(), None).to_dict("records")
