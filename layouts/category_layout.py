from dash import Dash, html, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from utils.chart_helpers import categories_df
import json
import plotly.express as px
import dash
import requests

def parse_data(categories_df):
    categories_df.loc[:, 'top_3_coins'] = categories_df['top_3_coins'].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x
    )
    return categories_df
def generate_category_visualization(categories_df):
    categories_df = categories_df[(categories_df['market_cap'] > 0) & (categories_df['market_cap'].notna())].copy()
    categories_df.loc[:, 'market_cap_24h_change'] = categories_df['market_cap_24h_change'].fillna(0)
    categories_df.loc[:, 'volume_24h'] = categories_df['volume_24h'].fillna(0)

    # bar chart for Market Cap and Volume
    bar_chart_fig = go.Figure(data=[
        go.Bar(
            x=categories_df['name'],
            y=categories_df['market_cap'],
            name='Market Cap',
            marker_color='blue'
        ),
        go.Bar(
            x=categories_df['name'],
            y=categories_df['volume_24h'],
            name='24h Volume',
            marker_color='orange'
        )
    ])
    bar_chart_fig.update_layout(
        title="Market Cap and 24h Volume by Category",
        barmode='group',
        xaxis_title="Category",
        yaxis_title="Value (USD)",
        template='plotly_white'
    )

    return bar_chart_fig


def generate_category_table(categories_df):
    # Filter and sort categories by market cap (top 50)
    categories_df = categories_df[(categories_df['market_cap'] > 0) & categories_df['market_cap'].notna()]
    top_categories_df = categories_df.nlargest(50, 'market_cap')

    # table columns
    table_columns = [
        {"name": "Category", "id": "name"},
        {"name": "Market Cap (B)", "id": "market_cap"},
        {"name": "Market Cap Change (24h, %)", "id": "market_cap_24h_change"},
        {"name": "Volume 24h (B)", "id": "volume_24h"},
        {"name": "Top 3 Coins", "id": "top_3_coins", "presentation": "markdown"},
    ]

    # table data
    table_data = []
    for _, row in top_categories_df.iterrows():
        coin_images = "".join([f"![coin]({url})" for url in row['top_3_coins']])
        table_data.append({
            "name": row['name'],
            "market_cap": f"${row['market_cap'] / 1e9:.2f}B",
            "market_cap_24h_change": f"{row['market_cap_24h_change']:.2f}%",
            "volume_24h": f"${row['volume_24h'] / 1e9:.2f}B",
            "top_3_coins": coin_images
        })

    #  style data conditional to color cells based on market_cap_24h_change value
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{market_cap_24h_change} <= 0',
                'column_id': 'market_cap_24h_change'
            },
            'color': 'red',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{market_cap_24h_change} >= 0',
                'column_id': 'market_cap_24h_change'
            },
            'color': 'green',
            'fontWeight': 'bold'
        },
    ]

    # DataTable
    category_table = dash_table.DataTable(
        id='category-table',
        columns=table_columns,
        data=table_data,
        style_table={'overflowX': 'auto', 'width': '100%'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '14px'
        },
        style_data_conditional=style_data_conditional,
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        markdown_options={"html": True},
        page_size=30
    )

    return html.Div([category_table])

categories_df = parse_data(categories_df)

bar_chart_fig = generate_category_visualization(categories_df)
category_table = generate_category_table(categories_df)


category_layout = html.Div([
    html.H4("Top 30 Categories by Market Cap"),
    category_table,
    dcc.Graph(figure=bar_chart_fig),
])
