"""Dash application factory. Gunicorn serves `betting_dashboard.app:server`."""

from __future__ import annotations

import logging
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, html

from betting_dashboard.components.layout import footer, navbar, page_header
from betting_dashboard.components.theme import register_template
from betting_dashboard.config import settings
from betting_dashboard.data import store

# Vendored so the site makes no third-party requests. Listed explicitly (and excluded from
# Dash's automatic asset loading) so they load before assets/style.css.
VENDOR_CSS = [
    "/assets/vendor/bootstrap/bootstrap.min.css",
    "/assets/vendor/bootstrap-icons/bootstrap-icons.min.css",
    "/assets/vendor/inter/inter.css",
]

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
        {%css%}
    </head>
    <body data-ag-theme-mode="dark">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


def not_found(**_query: str) -> html.Div:
    return html.Div(
        [
            page_header("Page not found", "That page doesn't exist, or it moved in the redesign."),
            dbc.Button("Back to the overview", href="/", color="warning"),
        ]
    )


def create_app() -> Dash:
    register_template()
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder="",
        assets_folder=str(Path(__file__).parent / "assets"),
        assets_path_ignore=["vendor"],
        external_stylesheets=VENDOR_CSS,
        title=settings.app_name,
        update_title=None,
        compress=True,
        # Pages are registered explicitly; skipping the validation layout keeps every page's
        # data out of the initial HTML.
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"name": "theme-color", "content": "#0b1220"},
        ],
    )
    app.index_string = INDEX_TEMPLATE

    from betting_dashboard.pages import PAGES

    for order, page in enumerate(PAGES):
        dash.register_page(
            page.__name__,
            path=page.PATH,
            name=page.NAME,
            title=f"{page.TITLE} · {settings.app_name}",
            description=page.DESCRIPTION,
            layout=page.layout,
            order=order,
        )
    dash.register_page("not_found_404", path="/404", layout=not_found)

    app.layout = html.Div(
        [
            navbar(),
            html.Main(dbc.Container(dash.page_container, fluid="xl"), className="app-main"),
            footer(),
        ],
        className="app-shell",
    )

    @app.callback(
        Output("nav-collapse", "is_open"),
        Input("nav-toggler", "n_clicks"),
        State("nav-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_nav(_n, is_open):
        return not is_open

    @app.server.get("/healthz")
    def healthz():
        return {
            "status": "ok",
            "games": len(store.games()),
            "predictions": len(store.predictions()),
        }

    # Warm the caches so the first visitor doesn't pay for parquet reads.
    store.games(), store.predictions(), store.upcoming()
    logging.getLogger(__name__).info("App ready: %s", settings.app_name)
    return app


app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(debug=settings.debug, host="0.0.0.0", port=8050)
