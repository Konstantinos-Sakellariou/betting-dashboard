"""AG Grid defaults and column helpers."""

from __future__ import annotations

from typing import Any

import dash_ag_grid as dag


def _fmt(expr: str) -> dict[str, str]:
    return {"function": f"params.value == null ? '—' : {expr}"}


FMT_PCT = _fmt("d3.format('.1%')(params.value)")
FMT_SIGNED_PCT = _fmt("d3.format('+.1%')(params.value)")
FMT_UNITS = _fmt("d3.format('+.2f')(params.value) + 'u'")
FMT_ODDS = _fmt("d3.format('.2f')(params.value)")
FMT_1DP = _fmt("d3.format('.1f')(params.value)")
FMT_INT = _fmt("d3.format(',')(params.value)")

RESULT_CLASSES = {
    "cell-win": "params.value === 'win'",
    "cell-loss": "params.value === 'loss'",
    "cell-push": "params.value === 'push'",
}
SIGN_CLASSES = {"cell-win": "params.value > 0", "cell-loss": "params.value < 0"}


def col(field: str, header: str, **kwargs: Any) -> dict[str, Any]:
    return {"field": field, "headerName": header, **kwargs}


def text_col(field: str, header: str, **kwargs: Any) -> dict[str, Any]:
    return col(field, header, **{"filter": "agTextColumnFilter", **kwargs})


def num_col(field: str, header: str, fmt: dict | None = None, **kwargs: Any) -> dict[str, Any]:
    extra = {"valueFormatter": fmt} if fmt else {}
    return col(
        field, header, filter="agNumberColumnFilter", type="numericColumn", **extra, **kwargs
    )


def date_col(field: str = "date", header: str = "Date", **kwargs: Any) -> dict[str, Any]:
    return col(
        field,
        header,
        filter="agDateColumnFilter",
        filterParams={"browserDatePicker": True},
        minWidth=120,
        **kwargs,
    )


def result_col(field: str, header: str = "Result", **kwargs: Any) -> dict[str, Any]:
    return text_col(field, header, cellClassRules=RESULT_CLASSES, minWidth=100, **kwargs)


def data_grid(
    id: str,
    column_defs: list[dict[str, Any]],
    row_data: list[dict[str, Any]] | None = None,
    *,
    height: int = 520,
    infinite: bool = False,
    grid_options: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dag.AgGrid:
    options: dict[str, Any] = {
        "animateRows": False,
        "suppressCellFocus": True,
        "enableCellTextSelection": True,
        "tooltipShowDelay": 300,
    }
    if infinite:
        options |= {"cacheBlockSize": 100, "maxBlocksInCache": 20, "rowBuffer": 20}
    else:
        options |= {
            "pagination": True,
            "paginationPageSize": 25,
            "paginationPageSizeSelector": [25, 50, 100],
        }
    options |= grid_options or {}

    extra: dict[str, Any] = {"rowModelType": "infinite"} if infinite else {"rowData": row_data}
    return dag.AgGrid(
        id=id,
        columnDefs=column_defs,
        defaultColDef={
            "sortable": True,
            "resizable": True,
            "filter": True,
            "floatingFilter": True,
            "minWidth": 90,
            "flex": 1,
        },
        dashGridOptions=options,
        className="grid",
        style={"height": f"{height}px", "width": "100%"},
        **extra,
        **kwargs,
    )
