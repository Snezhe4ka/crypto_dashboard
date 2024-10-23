from dash import html, dcc, dash_table
from utils.chart_helpers import (
    market_df, global_df, trending_df, dominance_df, gainers_df, volume_df,
    generate_global_charts, generate_dominance_pie_chart, generate_global_overview,  create_top_trending_cards, volume_chart,  treemap,  create_market_table
)
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objs as go

global_cards, fig_market_cap, fig_volume = generate_global_overview(global_df)

index_layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=generate_dominance_pie_chart(dominance_df))
            ], width=4,
            ),
            dbc.Col([
                html.H4("Top Trending Coins"),
                create_top_trending_cards(trending_df)
            ], width=8),
        ], className="my-4"),

        dbc.Row([
            global_cards
        ], className="my-4"),

        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=treemap(market_df))
            ], width=12, style={"padding-left": "0.5%", "padding-right": "0.5%"}
            ),
        ], className="my-4"),

        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id="gainers-line-chart",
                    figure={
                        'data': [
                            go.Scatter(
                                x=[row['symbol']],
                                y=[row['market_cap']],
                                mode='lines+markers',
                                name=row['symbol'],
                                line={'color': px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]}
                            ) for i, row in gainers_df.iterrows()
                        ],
                        'layout': go.Layout(
                            title='Top Gainers by Market Cap',
                            xaxis={'title': 'Cryptocurrency'},
                            yaxis={'title': 'Market Cap'},
                            showlegend=True,
                            template='plotly_white'
                        )
                    }
                )
            ], width=6),
            dbc.Col([
                volume_chart(volume_df)
                ], width=6),
        ], className="my-4"),

        dbc.Row([
            dbc.Col([
                html.H4("Cryptocurrency Market Overview", className="text-center my-4"),
                html.Div([create_market_table(market_df)])  # Ensure the function returns a valid DataTable component
            ])
        ], className="my-4"),
    ], fluid=True),
])




