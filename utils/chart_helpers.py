import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dash_table, dcc
import plotly.express as px
import dash
import pandas as pd
import requests
import json
from data.db_manager import (
    SessionLocal, MarketData, TopGainersMarketCap, TopProjectsByVolume,
    GlobalData, MarketDominance, TrendingCoins, Categories
)

def fetch_data_from_db():
    session = SessionLocal()
    try:
        # Fetch Market Data
        market_data = session.query(MarketData).all()
        market_df = pd.DataFrame([{
            'id': coin.id,
            'symbol': coin.symbol,
            'name': coin.name,
            'image': coin.image,
            'current_price': coin.current_price,
            'market_cap': coin.market_cap,
            'market_cap_rank': coin.market_cap_rank,
            'fully_diluted_valuation': coin.fully_diluted_valuation,
            'total_volume': coin.total_volume,
            'high_24h': coin.high_24h,
            'low_24h': coin.low_24h,
            'price_change_24h': coin.price_change_24h,
            'price_change_percentage_24h': coin.price_change_percentage_24h,
            'market_cap_change_24h': coin.market_cap_change_24h,
            'market_cap_change_percentage_24h': coin.market_cap_change_percentage_24h,
            'circulating_supply': coin.circulating_supply,
            'total_supply': coin.total_supply,
            'max_supply': coin.max_supply,
            'ath': coin.ath,
            'ath_change_percentage': coin.ath_change_percentage,
            'ath_date': coin.ath_date,
            'atl': coin.atl,
            'atl_change_percentage': coin.atl_change_percentage,
            'atl_date': coin.atl_date,
            # 'roi': coin.roi,
            'last_updated': coin.last_updated,
            'price_change_percentage_1h': coin.price_change_percentage_1h,
            # 'sparkline_in_7d': coin.sparkline_in_7d,
            'timestamp': coin.timestamp
        } for coin in market_data])

        # Fetch Top Gainers
        top_gainers = session.query(TopGainersMarketCap).all()
        gainers_df = pd.DataFrame([{
            'id': gainer.id,
            'name': gainer.name,
            'symbol': gainer.symbol,
            'price': gainer.price,
            'change_24h': gainer.change_24h,
            'percent_change_7d': gainer.percent_change_7d,
            'market_cap_change_percentage_24h': gainer.market_cap_change_percentage_24h,
            'market_cap': gainer.market_cap,
            'market_cap_dominance': gainer.market_cap_dominance,
            'date_added': gainer.date_added,
            'data_period': gainer.data_period,
            'timestamp': gainer.timestamp
        } for gainer in top_gainers if gainer.symbol.lower() not in ['usdt', 'usdc']])

        # Fetch Top Projects By Volume
        top_volume = session.query(TopProjectsByVolume).all()
        volume_df = pd.DataFrame([{
            'id': project.id,
            'name': project.name,
            'symbol': project.symbol,
            'total_volume': project.total_volume,
            'market_cap': project.market_cap,
            'last_updated': project.last_updated,
            'timestamp': project.timestamp
        } for project in top_volume if project.symbol.lower() not in ['usdt', 'usdc']])


        # Fetch Global Data
        global_data = session.query(GlobalData).all()
        global_df = pd.DataFrame([{
            'id': data.id,
            'active_cryptocurrencies': data.active_cryptocurrencies,
            'upcoming_icos': data.upcoming_icos,
            'ongoing_icos': data.ongoing_icos,
            'ended_icos': data.ended_icos,
            'markets': data.markets,
            'total_market_cap': data.total_market_cap,
            'total_volume': data.total_volume,
            'market_cap_percentage': data.market_cap_percentage,
            'market_cap_change_percentage_24h_usd': data.market_cap_change_percentage_24h_usd,
            'updated_at': data.updated_at,
            'timestamp': data.timestamp
        } for data in global_data])

        # Fetch Market Dominance Data
        dominance_data = session.query(MarketDominance).all()
        dominance_df = pd.DataFrame([{
            'id': dom.id,
            'btc': dom.btc,
            'eth': dom.eth,
            'usdt': dom.usdt,
            'usdc': dom.usdc,
            'bnb': dom.bnb,
            'sol': dom.sol,
            'xrp': dom.xrp,
            'others': dom.others,
            'timestamp': dom.timestamp
        } for dom in dominance_data])

        # Fetch Trending Coins
        trending_data = session.query(TrendingCoins).all()


        trending_df = pd.DataFrame([{
            'id': coin.id,
            'coin_id': coin.coin_id,
            'coin_name': coin.coin_name,
            'symbol': coin.symbol,
            'market_cap_rank': coin.market_cap_rank,
            'small': coin.small,
            'score': coin.score,
            'price': coin.price,
            'market_cap': coin.market_cap,
            'total_volume': coin.total_volume,
            'timestamp': coin.timestamp
        } for coin in trending_data])


        # Fetch Categories Data
        category_data = session.query(Categories).all()
        categories_df = pd.DataFrame([{
            'id': category.id,
            'category_id': category.category_id,
            'name': category.name,
            'market_cap': category.market_cap,
            'market_cap_24h_change': category.market_cap_24h_change,
            'top_3_coins': category.top_3_coins,
            'volume_24h': category.volume_24h,
            'timestamp': category.timestamp
        } for category in category_data])

        return market_df, gainers_df, volume_df, global_df, dominance_df, trending_df, categories_df

    finally:
        session.close()

# Fetch data
market_df, gainers_df, volume_df, global_df, dominance_df, trending_df, categories_df = fetch_data_from_db()


def generate_global_charts(global_df):
    # Analyze and visualize key metrics from global_df
    fig_market_cap = go.Figure()
    fig_market_cap.add_trace(go.Bar(
        x=list(global_df['total_market_cap'].iloc[-1].keys()),  # Extract currencies
        y=list(global_df['total_market_cap'].iloc[-1].values()),  # Extract market cap values
        name='Total Market Cap'
    ))
    fig_market_cap.update_layout(
        title="Total Market Cap by Currency",
        xaxis_title="Currency",
        yaxis_title="Market Cap (in USD)",
    )
    return fig_market_cap


def create_top_trending_cards(trending_df):

    trending_df['market_cap'] = pd.to_numeric(trending_df['market_cap'], errors='coerce')

    top_trending_df = trending_df.nlargest(12, 'market_cap')
    cards = []
    for _, row in top_trending_df.iterrows():
        icon_url = row['small']
        # Create a card for each gainer
        card = dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.Img(src=icon_url,  style={"margin-right": "3px"}),
                    html.H5(f"{row['coin_name']}", className="card-title"),
                ], className="d-flex align-items-center d-flex1"),
                html.P(f"Price: ${row['price']:,.2f}", className="card-text", style={"font-size": "14px"}),
                html.P(f"Market Cap: ${row['market_cap'] / 1e9:.2f}B", className="card-text",
                       style={"font-size": "14px"}),
            ]),
            className="m-1 shadow-sm",
            style={"width": "160px", "height": "160px", "margin-right": "5px"}
        )
        cards.append(card)

    return dbc.Row([dbc.Col(card, width=2) for card in cards], className="g-1")


def generate_dominance_pie_chart(dominance_df):
    # Visualize market dominance as a pie chart
    labels = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'SOL', 'XRP', 'Others']
    values = [
        dominance_df['btc'].iloc[-1],
        dominance_df['eth'].iloc[-1],
        dominance_df['usdt'].iloc[-1],
        dominance_df['usdc'].iloc[-1],
        dominance_df['bnb'].iloc[-1],
        dominance_df['sol'].iloc[-1],
        dominance_df['xrp'].iloc[-1],
        dominance_df['others'].iloc[-1]
    ]

    fig_dominance_pie = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.3
    ))
    fig_dominance_pie.update_layout(
        title="Market Dominance Distribution"
    )

    # return figure
    return fig_dominance_pie


def treemap(market_df):
    if not isinstance(market_df, pd.DataFrame):
        raise ValueError("market_df should be a pandas DataFrame.")

    market_df['market_cap'] = pd.to_numeric(market_df['market_cap'], errors='coerce')
    filtered_df = market_df[market_df['market_cap'] > 0].dropna(subset=['market_cap'])

    # treemap with market cap size and percentage change in price as color
    fig = px.treemap(
        filtered_df,
        path=['name', 'symbol'],
        values='market_cap',
        color='price_change_percentage_24h',  # color based on 24h price change
        hover_data={
            'market_cap': ':,.2f',
            'current_price': ':,.2f',
            'price_change_percentage_24h': ':.2f',  # format 24h price change
            'total_volume': ':,.2f'  # format total volume
        },
        color_continuous_scale='RdYlGn',  # a red-yellow-green color scale for price change
        title='Cryptocurrency Market Cap Treemap'
    )

    # layout for better visualization and full screen
    fig.update_layout(
        margin=dict(t=50, l=0, r=0, b=0),
        title_font_size=24,
        height=None,
        width=None,
        autosize=True,
        coloraxis_colorbar=dict(
            title='24H Price Change (%)',
            ticks="outside",
            tickvals=[-15, -10, -5, 0, 5, 10, 15],
            ticktext=["-15%", "-10%", "-5%", "0%", "+5%", "+10%", "+15%"]
        )
    )

    return fig


dcc.Graph(figure=treemap(market_df), style={'height': '95vh', 'width': '84vw'})


def format_currency(value):
    """Formats number as currency."""
    if pd.isnull(value):
        return "-"
    try:
        return f"${value:,.2f}"
    except Exception as e:
        print(f"Error formatting currency: {e}, value: {value}")
        return "-"


def format_percentage(value):
    """Formats number as percentage."""
    if pd.isnull(value):
        return "-"
    try:
        return f"{value:+.2f}%"
    except Exception as e:
        print(f"Error formatting percentage: {e}, value: {value}")
        return "-"


def format_large_numbers(value):
    """Formats large numbers (e.g., market cap, volume)."""
    if pd.isnull(value):
        return "-"
    try:
        if value >= 1e9:
            return f"{value / 1e9:.2f}B"
        elif value >= 1e6:
            return f"{value / 1e6:.2f}M"
        else:
            return f"{value:,.0f}"
    except Exception as e:
        print(f"Error formatting large number: {e}, value: {value}")
        return "-"


def create_market_table(market_df):
    # copy of the DataFrame
    # market_df2 = market_df.drop(columns=['sparkline_in_7d', 'roi'], errors='ignore').copy()
    market_df2 = market_df.copy()

    # format columns
    market_df2['formatted_price'] = market_df2['current_price'].apply(format_currency)
    market_df2['formatted_price_change_24h'] = market_df2['price_change_percentage_24h'].apply(format_percentage)
    market_df2['formatted_market_cap'] = market_df2['market_cap'].apply(format_large_numbers)
    market_df2['formatted_total_volume'] = market_df2['total_volume'].apply(format_large_numbers)

    # select columns to display in the table
    table_columns = [
        {'name': 'Asset', 'id': 'name', 'presentation': 'markdown'},  # Markdown column for Asset
        {'name': 'Price (Live)', 'id': 'formatted_price'},
        {'name': 'Price 24H % Chg', 'id': 'formatted_price_change_24h'},
        {'name': 'Real Vol 24H Sum', 'id': 'formatted_total_volume'},
        {'name': 'Mcap Today', 'id': 'formatted_market_cap'},
        {'name': 'ATH', 'id': 'ath'}
    ]

    # Data for the table from the modified DataFrame
    table_data = market_df2.to_dict('records')

    # Return the Dash DataTable
    return dash_table.DataTable(
        id='market-table',
        columns=table_columns,
        data=table_data,
        style_cell={'textAlign': 'left', 'fontSize': '14px', 'padding': '10px'},
        style_data_conditional=[
            # Conditional formatting for price change column
            {
                'if': {
                    'filter_query': '{formatted_price_change_24h} contains "-"',
                    'column_id': 'formatted_price_change_24h'
                },
                'color': 'red'
            },
            {
                'if': {
                    'filter_query': '{formatted_price_change_24h} contains "+"',
                    'column_id': 'formatted_price_change_24h'
                },
                'color': 'green'
            },
        ],
        style_header={
            'backgroundColor': 'white',
            'color': 'black',
            'fontWeight': 'bold',
            'border': '1px solid black'
        },
        style_table={'overflowX': 'auto', 'width': '100%'},
        style_data={
            'backgroundColor': 'white',
            'color': 'black',
            'border': '1px solid #ddd'
        },
        markdown_options={"html": True},
        page_size=20,
    )


coins = ["btc", "eth", "sol", "bnb", "aave", "apt", "pepe"]


# def volume_chart(volume_df):
#     # Ensure 'total_volume' column is numeric
#     volume_df['total_volume'] = pd.to_numeric(volume_df['total_volume'], errors='coerce')
#
#     # Filter the top 20 projects by volume (or use your own logic)
#     top_volume_df = volume_df.nlargest(20, 'total_volume')
#
#     # Create the line chart for each project
#     figure = {
#         'data': [
#             go.Scatter(
#                 x=[row['name']],  # X-axis as the project name
#                 y=[row['total_volume']],  # Y-axis as the total volume
#                 mode='lines+markers',  # Show both lines and markers
#                 name=row['name'],  # Label each line with the project's name
#                 line={'color': px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]}
#             ) for i, row in top_volume_df.iterrows()
#         ],
#         'layout': go.Layout(
#             title='Top Projects by Volume',
#             xaxis={'title': 'Project'},
#             yaxis={'title': 'Total Volume'},
#             showlegend=True,
#             template='plotly_white'
#         )
#     }
#
#     # Return the Dash Graph component with the figure
#     return dcc.Graph(
#         id="volume-line-chart",
#         figure=figure
#     )

def volume_chart(volume_df):
    # Ensure 'total_volume' column is numeric
    volume_df['total_volume'] = pd.to_numeric(volume_df['total_volume'], errors='coerce')

    # Sort the DataFrame by total volume
    volume_df = volume_df.sort_values('total_volume', ascending=False)

    # Create the bar chart using Plotly Express
    fig = px.bar(
        volume_df,
        x='name',
        y='total_volume',
        color='name',
        text='total_volume',
        title="Top Projects by Volume",
        labels={'name': 'Project', 'total_volume': 'Total Volume'}
    )

    # Update layout for clarity and appearance
    fig.update_layout(
        xaxis_title="Project",
        yaxis_title="Total Volume",
        showlegend=False,
        template='plotly_white'
    )

    # Add hover info for better user interaction
    fig.update_traces(
        texttemplate='%{text:.2s}',
        textposition='outside',
        hovertemplate="Project: %{x}<br>Total Volume: %{y:.2f}"
    )

    # Return the Dash Graph component with the figure
    return dcc.Graph(
        id="volume-bar-chart",
        figure=fig
    )

def parse_global_data(global_df):
    # Parse total market cap and total volume as they are stored as JSON strings
    global_df['total_market_cap'] = global_df['total_market_cap'].apply(json.loads)
    global_df['total_volume'] = global_df['total_volume'].apply(json.loads)
    global_df['market_cap_percentage'] = global_df['market_cap_percentage'].apply(json.loads)
    return global_df

def generate_global_overview(global_df):
    # Select the latest data (assuming the latest entry is the most recent one)
    latest_data = global_df.iloc[-1]

    # Cards for displaying key statistics
    cards = dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Active Cryptocurrencies", className="card-title"),
                html.P(f"{latest_data['active_cryptocurrencies']}", className="card-text")
            ]),
            className="m-2 shadow-sm"
        ), width=3),

        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H5("Markets", className="card-title"),
                html.P(f"{latest_data['markets']}", className="card-text")
            ]),
            className="m-2 shadow-sm"
        ), width=3),

        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H5("Market Cap Change (24h)", className="card-title"),
                html.P(f"{latest_data['market_cap_change_percentage_24h_usd']:.2f}%", className="card-text")
            ]),
            className="m-2 shadow-sm"
        ), width=3),
    ], className="my-4")

    # Graphs for total market cap and volume
    market_cap_data = latest_data['total_market_cap']
    volume_data = latest_data['total_volume']
    labels = list(market_cap_data.keys())
    market_cap_values = list(market_cap_data.values())
    volume_values = list(volume_data.values())

    # Pie chart for market cap distribution
    fig_market_cap = go.Figure(data=[go.Pie(
        labels=labels,
        values=market_cap_values,
        hole=0.4
    )])
    fig_market_cap.update_layout(title="Market Cap Distribution")

    # Bar chart for total volume
    fig_volume = go.Figure(data=[go.Bar(
        x=labels,
        y=volume_values
    )])
    fig_volume.update_layout(title="Total Volume Distribution", xaxis_title="Currency", yaxis_title="Volume")

    return cards, fig_market_cap, fig_volume


global_cards, fig_market_cap, fig_volume = generate_global_overview(global_df)


categories_df


def parse_data(categories_df):
    # Parsing the JSON-like columns for icons
    categories_df['top_3_coins'] = categories_df['top_3_coins'].apply(lambda x: json.loads(x.replace("'", '"')))
    categories_df['market_cap'] = pd.to_numeric(categories_df['market_cap'])
    categories_df['market_cap_24h_change'] = pd.to_numeric(categories_df['market_cap_24h_change'])
    categories_df['volume_24h'] = pd.to_numeric(categories_df['volume_24h'])
    return categories_df


categories = parse_data(categories_df)

# 1. Treemap Visualization
def create_treemap(categories):
    fig = px.treemap(categories,
                     path=['name'],
                     values='market_cap',
                     color='market_cap_24h_change',
                     color_continuous_scale='RdYlGn',
                     title='Market Cap Distribution by Category')
    return fig

# 2. Bar Chart for Market Cap Change
def create_market_cap_change_bar(categories):
    fig = px.bar(df,
                 x='name',
                 y='market_cap_24h_change',
                 color='market_cap_24h_change',
                 color_continuous_scale='RdYlGn',
                 title='24h Market Cap Change by Category')
    fig.update_layout(xaxis_title='Category', yaxis_title='24h Change (%)', template='plotly_white')
    return fig

# 3. Scatter Plot for Market Cap vs Volume
def create_scatter_plot(categories):
    fig = px.scatter(categories,
                     x='market_cap',
                     y='volume_24h',
                     size='market_cap',
                     color='market_cap_24h_change',
                     hover_name='name',
                     title='Market Cap vs. 24h Trading Volume',
                     color_continuous_scale='RdYlGn',
                     log_x=True,
                     log_y=True)
    fig.update_layout(xaxis_title='Market Cap (Log Scale)', yaxis_title='24h Volume (Log Scale)', template='plotly_white')
    return fig

# 4. Carousel of Top Coins per Category
def create_top_coins_carousel(categories):
    cards = []
    for _, row in categories.iterrows():
        coin_images = [html.Img(src=coin, height='40px', style={'margin-right': '5px'}) for coin in row['top_3_coins']]
        card = dbc.Card(
            dbc.CardBody([
                html.H5(row['name'], className='card-title'),
                html.Div(coin_images, className='d-flex align-items-center'),
            ]),
            className='m-2 shadow-sm',
            style={'width': '200px', 'height': '150px'}
        )
        cards.append(card)
    return dbc.Row([dbc.Col(card, width=4) for card in cards])


# def create_top_gainers_cards(gainers_df):
#     # Filter the top 10 gainers based on market cap or any other criteria
#     top_gainers_df = gainers_df.nlargest(12, 'market_cap')  # Top 10 by market cap
#
#     cards = []
#     for _, row in top_gainers_df.iterrows():
#         icon_url = row['symbol']
#
#         # Set a default icon URL if the fetched icon doesn't work (Fallback icon URL)
#         default_icon_url = "https://cryptologos.cc/logos/default-logo.png"  # Replace with a valid fallback URL
#
#     # Create a card for each gainer
#         card = dbc.Card(
#             dbc.CardBody([
#                 html.Div([
#                     html.Img(src=icon_url, height="10px", style={"margin-right": "5px"}),
#                     html.H5(f"{row['name']} ({row['symbol'].upper()})", className="card-title"),
#                 ], className="d-flex align-items-center"),
#                 html.P(f"Price: ${row['price']:,.2f}", className="card-text"),
#                 html.P(f"Market Cap: ${row['market_cap'] / 1e9:.2f}B", className="card-text"),
#                 html.P(f"24H Change: {round(row['change_24h'], 2)}%", className="card-text text-success"
#                 if row['change_24h'] > 0 else "card-text text-danger"),
#             ]),
#             className="m-2 shadow-sm",
#             style={"width": "250px"}
#         )
#         cards.append(card)
#
#     return dbc.Row([dbc.Col(card, width=4) for card in cards], className="my-4")
#
# def layout(global_df, trending_df, dominance_df, market_df):
#     return html.Div([
#         html.H2("Cryptocurrency Global Data Overview"),
#         generate_global_charts(global_df),
#         html.H2("Trending Coins Analysis"),
#         # generate_trending_charts(trending_df),
#         html.H2("Market Dominance"),
#         generate_dominance_pie_chart(dominance_df),
#
#
#     ])


#
#
# if __name__ == "__main__":
#     layout(global_df, trending_df, dominance_df, market_df)



# # trending coins cards
# def create_trending_coins_cards(trending_df):
#     if not isinstance(trending_df, list):
#         return html.Div("No trending coins data available.", style={"color": "red"})
#
#     coin_cards = []
#
#     for coin in trending_df:
#         coin_name = coin.get('name', 'Unknown Coin')
#         coin_symbol = coin.get('symbol')
#         market_cap_rank = coin.get('market_cap_rank')
#         icon_url = coin.get('small', get_icon_url(coin_symbol))
#
#         card = dbc.Card(
#             dbc.CardBody([
#                 html.Img(src=icon_url, style={"height": "40px", "width": "40px"}),
#                 html.H5(f"{coin_name} ({coin_symbol})", className="card-title"),
#                 html.P(f"Market Cap Rank: {market_cap_rank}", className="card-text"),
#             ]),
#             className="mb-3"
#         )
#         coin_cards.append(card)
#
#     if not coin_cards:
#         return html.Div("No trending coins data available.", style={"color": "red"})
#
#     # Organize the cards into rows of two columns
#     rows = []
#     for i in range(0, len(coin_cards), 6):
#         row = dbc.Row([
#             dbc.Col(coin_cards[i], width=3),
#             dbc.Col(coin_cards[i], width=3),
#             dbc.Col(coin_cards[i], width=3),
#             dbc.Col(coin_cards[i], width=3),
#             dbc.Col(coin_cards[i], width=3),
#             dbc.Col(coin_cards[i + 1], width=3) if i + 1 < len(coin_cards) else None
#         ])
#         rows.append(row)
#
#     return html.Div(rows, style={"margin-top": "10px"})


# #gauge chart for Fear and Greed Index and Bitcoin Dominance
# def create_gauge_chart(title, value, max_value):
#     fig = go.Figure(go.Indicator(
#         mode="gauge+number",
#         value=value,
#         gauge={
#             'axis': {'range': [0, max_value]},
#             'bar': {'color': "#659EC7"},  # Set the color here
#             'steps': [
#                 {'range': [0, value], 'color': "#659EC7"}
#             ]
#         },
#         domain={'x': [0, 1], 'y': [0, 1]}
#     ))
#     fig.update_layout(title=title)
#     return fig
#
#
# # Create the Top Gainers bar chart
# def create_top_gainers_chart(selected_period, df):
#     if df is not None and not df.empty:
#         fig = go.Figure(data=[go.Bar(
#             x=df['name'],
#             y=df[f'change_{selected_period}'],
#             marker_color='#659EC7'
#         )])
#         fig.update_layout(title=f'Top Gainers ({selected_period})')
#     else:
#         print(f"No data available for the selected period: {selected_period}.")
#         fig = go.Figure()
#         fig.update_layout(title=f'No Data Available for {selected_period}')
#
#     return fig
#
#
# def create_project_details_section(project_data):
#     if not project_data:
#         return html.Div("No data available for the selected project.", style={"color": "red"})
#
#     details = [
#         html.H4(f"{project_data.get('name', 'N/A')} ({project_data.get('symbol', 'N/A')})"),
#         html.P(f"Market Cap: ${project_data.get('market_cap', 0):,.2f}"),
#         html.P(f"Price: ${project_data.get('price', 0):,.2f}"),
#         html.P(f"Change 24H: {project_data.get('change_24h', 0):.2f}%"),
#         html.P(f"Total Supply: {project_data.get('total_supply', 'N/A')}"),
#         html.P(f"Circulating Supply: {project_data.get('circulating_supply', 'N/A')}"),
#         html.P(f"Max Supply: {project_data.get('max_supply', 'N/A')}")
#     ]
#
#     return html.Div(details, style={"padding": "20px", "backgroundColor": "#f9f9f9", "borderRadius": "5px"})
#
#
#
# def create_top_gainers_table(top_gainers_data):
#     columns = [
#         {"name": "Name", "id": "name", "presentation": "markdown"},
#         {"name": "Change 24H", "id": "change_24h"},
#         {"name": "Rank", "id": "rank"},
#         {"name": "Broker Score", "id": "broker_score"},
#         {"name": "Price", "id": "price"},
#         {"name": "Public ROI", "id": "public_roi"},
#     ]
#
#     data = [
#         {
#             "name": f"![{row['name']}]({get_icon_url(row['name'])})",
#             "change_24h": row.get("change_24h", "N/A"),
#             "rank": row.get("rank", "N/A"),
#             "broker_score": row.get("broker_score", "N/A"),
#             "price": row.get("price", "N/A"),
#             "public_roi": row.get("public_roi", "N/A")
#         }
#         for row in top_gainers_data
#     ]
#
#     table = dash_table.DataTable(
#         columns=columns,
#         data=data,
#         style_header={'backgroundColor': '#659EC7', 'color': 'white', 'fontWeight': 'bold'},
#         style_data={'color': '#659EC7', 'backgroundColor': 'white'},
#         style_cell={'textAlign': 'left', 'padding': '5px', 'whiteSpace': 'normal', 'height': 'auto'},
#         style_table={'overflowX': 'auto'},
#         markdown_options={'link_target': '_blank'},
#         filter_action="native",
#         sort_action="native",
#         sort_mode="multi",
#         page_action="native",
#         page_current=0,
#         page_size=10
#     )
#
#     return table
#
#
#
#
# def create_heatmap_chart(heatmap_data):
#     categories = [item['category'] for item in heatmap_data]
#     intensities = [item['intensity'] for item in heatmap_data]
#
#     fig = go.Figure(
#         data=go.Heatmap(
#             z=intensities,  # The "intensity" of the categories
#             x=categories,   # The category names
#             colorscale='Viridis'
#         )
#     )
#
#     fig.update_layout(
#         title="Cryptocurrency Categories Heatmap",
#         xaxis_title="Categories",
#         yaxis_title="Intensity (Market Cap)",
#         template="plotly_white"
#     )
#     return fig
#
#
# def create_projects_list_table(projects_data):
#     columns = [
#         {"name": "Name", "id": "name"},
#         {"name": "Change 24H", "id": "change_24h"},
#         {"name": "Rank", "id": "rank"},
#         {"name": "Broker Score", "id": "broker_score"},
#         {"name": "Price", "id": "price"},
#         # {"name": "Public Price", "id": "public_price"},
#         {"name": "Public ROI", "id": "public_roi"}
#
#     ]
#
#     table = dash_table.DataTable(
#         columns=columns,
#         data=projects_data,
#         style_header={
#             'backgroundColor': '#659EC7',
#             'color': 'white',
#             'fontWeight': 'bold'
#         },
#         style_data={
#             'color': '#659EC7',
#             'backgroundColor': 'white'
#         },
#         style_cell={
#             'textAlign': 'left',
#             'padding': '5px',
#             'whiteSpace': 'normal',
#             'height': 'auto'
#         },
#         style_table={'overflowX': 'auto'},
#         filter_action="native",
#         sort_action="native",
#         sort_mode="multi",
#         page_action="native",
#         page_current=3,
#         page_size=15  # Show 15 projects per page
#     )
#
#     return table
#
#
# def create_projects_list(projects_list):
#     return html.Ul([html.Li(f"{proj['name']} - Status: {proj['status']}") for proj in projects_list], style={"color": "#659EC7"})