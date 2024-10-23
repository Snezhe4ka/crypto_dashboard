from dash import html
import dash_bootstrap_components as dbc

sidebar = html.Div(
    [
        html.Div(
            [
                dbc.Nav(
                    [
                        dbc.NavLink([html.I(className="fas fa-chart-bar"), "Dashboard"], href="/dashboard", active="exact"),
                        dbc.NavLink([html.I(className="fas fa-chart-bar"), "Market Overview"], href="/dashboard/view",active="exact"),
                        dbc.NavLink([html.I(className="fas fa-th-large"), "Categories"], href="/dashboard/categories", active="exact"),
                    ],
                    vertical=True,
                    pills=True,
                ),
                html.Div(
                    dbc.Button("Update Data", id="update-data-button", color="primary", className="mt-3", style={"width": "100%"}),
                    className="d-grid gap-2"
                ),
                html.Div(id="update-status", className="mt-3", style={"color": "white"})
            ],
            className="sidebar",
            style={"background-color": "#659EC7", "color": "white", "height": "100vh"}
        ),
    ]
)
