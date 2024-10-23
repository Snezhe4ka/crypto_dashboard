from dash import html
from utils.chart_helpers import market_df, create_market_table
import dash_bootstrap_components as dbc

overview_layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H4("Cryptocurrency Market Overview", className="text-center my-4"),
            html.Div([create_market_table(market_df)])  # Ensure the function returns a valid DataTable component
        ])
    ])
])
