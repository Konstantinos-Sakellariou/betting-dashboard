"""Design tokens shared by CSS (assets/style.css mirrors these) and Plotly figures."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

BG = "#0b1220"
SURFACE = "#111a2e"
BORDER = "#1f2a44"
TEXT = "#e6ebf5"
MUTED = "#8a96b0"
GRID = "#1c2640"

ACCENT = "#f59e0b"  # basketball orange
WIN = "#22c55e"
LOSS = "#ef4444"
PUSH = "#94a3b8"
INFO = "#38bdf8"

# Categorical palette: accent first, then hues that stay distinct on a dark background.
PALETTE = [
    ACCENT,
    INFO,
    "#a78bfa",
    "#34d399",
    "#f472b6",
    "#facc15",
    "#60a5fa",
    "#fb7185",
    "#2dd4bf",
    "#c084fc",
    "#fdba74",
    "#a3e635",
    "#e879f9",
    "#93c5fd",
    "#fca5a5",
    "#5eead4",
]

FONT = "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"

TEMPLATE_NAME = "courtside"


def register_template() -> None:
    template = go.layout.Template(pio.templates["plotly_dark"])
    template.layout.update(
        font={"family": FONT, "color": TEXT, "size": 13},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=PALETTE,
        margin={"l": 48, "r": 16, "t": 24, "b": 40},
        hoverlabel={"bgcolor": SURFACE, "bordercolor": BORDER, "font": {"family": FONT}},
        legend={"bgcolor": "rgba(0,0,0,0)", "font": {"color": MUTED}},
        xaxis={"gridcolor": GRID, "zerolinecolor": BORDER, "linecolor": BORDER},
        yaxis={"gridcolor": GRID, "zerolinecolor": BORDER, "linecolor": BORDER},
    )
    pio.templates[TEMPLATE_NAME] = template
    pio.templates.default = TEMPLATE_NAME


GRAPH_CONFIG = {"displaylogo": False, "responsive": True, "modeBarButtonsToRemove": ["lasso2d"]}
