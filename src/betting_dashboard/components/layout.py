"""App shell and reusable building blocks for pages."""

from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html

from betting_dashboard.components.theme import GRAPH_CONFIG
from betting_dashboard.config import settings

NAV_ITEMS = [
    ("/", "Overview", "bi-speedometer2"),
    ("/predictions", "Predictions", "bi-bullseye"),
    ("/explorer", "Explorer", "bi-graph-up"),
    ("/teams", "Teams", "bi-people"),
    ("/games", "Game data", "bi-table"),
    ("/about", "About", "bi-info-circle"),
]


def icon(name: str, className: str = "") -> html.I:
    return html.I(className=f"bi {name} {className}".strip(), **{"aria-hidden": "true"})


def navbar() -> dbc.Navbar:
    links = [
        dbc.NavItem(dbc.NavLink([icon(ic, className="me-2"), label], href=href, active="exact"))
        for href, label, ic in NAV_ITEMS
    ]
    return dbc.Navbar(
        dbc.Container(
            [
                dcc.Link(
                    [
                        html.Span(icon("bi-dribbble"), className="brand-mark"),
                        html.Span(settings.app_name, className="brand-name"),
                    ],
                    href="/",
                    className="navbar-brand d-flex align-items-center gap-2",
                ),
                dbc.NavbarToggler(id="nav-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav(links, className="ms-auto", navbar=True),
                    id="nav-collapse",
                    navbar=True,
                ),
            ],
            fluid="xl",
        ),
        className="app-navbar",
        dark=True,
        sticky="top",
        expand="lg",
    )


def contact_links() -> list[tuple[str, str, str]]:
    """(label, href, icon) for each configured way to reach the author."""
    links = [
        ("Portfolio", settings.portfolio_url, "bi-globe2"),
        ("LinkedIn", settings.linkedin_url, "bi-linkedin"),
        ("GitHub", settings.github_url, "bi-github"),
        (
            "Email",
            f"mailto:{settings.contact_email}" if settings.contact_email else None,
            "bi-envelope",
        ),
    ]
    return [(label, href, ic) for label, href, ic in links if href]


def _external(label: str, href: str, ic: str) -> html.A:
    new_tab = {} if href.startswith("mailto:") else {"target": "_blank", "rel": "noopener"}
    return html.A([icon(ic, className="me-1"), label], href=href, **new_tab)


def footer() -> html.Footer:
    contact = [_external(*link) for link in contact_links()]
    contact.append(_external("Source code", settings.repo_url, "bi-code-slash"))
    return html.Footer(
        dbc.Container(
            [
                html.P(
                    [
                        html.Strong("For research and entertainment only. "),
                        "Past performance does not predict future results. Nothing here is "
                        "betting advice. 18+ only. If gambling stops being fun, get help at ",
                        html.A("BeGambleAware.org", href="https://www.begambleaware.org/"),
                        ".",
                    ],
                    className="disclaimer",
                ),
                html.Div(
                    [html.Span(f"Built by {settings.author_name}"), *contact],
                    className="footer-links",
                ),
            ],
            fluid="xl",
        ),
        className="app-footer",
    )


def page_header(title: str, subtitle: str | None = None, extra: Any = None) -> html.Div:
    return html.Div(
        [
            html.Div(
                [html.H1(title, className="page-title"), html.P(subtitle, className="page-sub")]
                if subtitle
                else [html.H1(title, className="page-title")]
            ),
            html.Div(extra, className="page-header-extra") if extra is not None else None,
        ],
        className="page-header",
    )


def card(
    children: Any, title: str | None = None, subtitle: str | None = None, **kwargs
) -> dbc.Card:
    header = None
    if title:
        header = html.Div(
            [html.H2(title, className="card-title-sm"), html.P(subtitle, className="card-sub")]
            if subtitle
            else [html.H2(title, className="card-title-sm")],
            className="panel-header",
        )
    body = list(children) if isinstance(children, list | tuple) else [children]
    return dbc.Card(
        dbc.CardBody([header, *body] if header else body),
        className="panel " + kwargs.pop("className", ""),
        **kwargs,
    )


def kpi(label: str, value: str, sub: Any = None, tone: str = "neutral", id: str | None = None):
    body = [
        html.Div(label, className="kpi-label"),
        html.Div(value, className=f"kpi-value tone-{tone}"),
        html.Div(sub, className="kpi-sub") if sub is not None else None,
    ]
    props = {"id": id} if id else {}
    return html.Div(body, className="kpi", **props)


def graph(id: str, height: int = 360, **kwargs: Any) -> dcc.Loading:
    return dcc.Loading(
        dcc.Graph(id=id, config=GRAPH_CONFIG, style={"height": f"{height}px"}, **kwargs),
        type="dot",
        color="#f59e0b",
        delay_show=250,
    )


def field(label: str, control: Any, width: dict[str, int] | None = None) -> dbc.Col:
    return dbc.Col(
        html.Div([dbc.Label(label, className="field-label"), control], className="field"),
        **(width or {"xs": 12, "md": 6, "lg": 3}),
    )


def dropdown(id: str, options: list[Any], value: Any = None, **kwargs: Any) -> dcc.Dropdown:
    return dcc.Dropdown(
        id=id,
        options=options,
        value=value,
        persistence=True,
        persistence_type="session",
        className="dd",
        **kwargs,
    )


def result_badge(result: str | None) -> html.Span:
    labels = {"win": ("Win", "bi-check-circle-fill"), "loss": ("Loss", "bi-x-circle-fill")}
    label, ic = labels.get(result or "", ("Push", "bi-dash-circle-fill"))
    return html.Span([icon(ic, className="me-1"), label], className=f"pill pill-{result}")


def empty_figure(message: str):
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font={"size": 14})
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig
