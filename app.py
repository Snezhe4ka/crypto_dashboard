from dash import Dash, dcc, html, callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output
from flask import Flask
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy.orm import Session
from layouts.sidebar import sidebar
from layouts.index_layout import index_layout
from layouts.category_layout import category_layout
from layouts.overview_layout import overview_layout
import matplotlib



matplotlib.use('Agg')

# Initialize Flask server
server = Flask(__name__)

# Initialize Dash app
app = Dash(__name__,
           server=server,
           url_base_pathname='/dashboard/',
           external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
           suppress_callback_exceptions=True)

# Define the app layout
app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=[
        html.Div(
            [
                dcc.Location(id='url', refresh=False),
                dbc.Row([
                    dbc.Col(sidebar, width=2, className="p-0"),
                    dbc.Col([
                        html.Div(id="page-content", style={"padding": "20px"})
                    ], width=10)
                ])
            ]
        )
    ]
)

# Routing logic
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    print(pathname)
    if pathname == '/dashboard':
        return index_layout
    elif pathname == '/dashboard/view':
        return overview_layout
    elif pathname == '/dashboard/categories':
        return category_layout
    else:
        return index_layout


if __name__ == '__main__':
    app.run_server(debug=True)
