


<img width="1793" alt="Screenshot 2024-10-23 at 08 43 06" src="https://github.com/user-attachments/assets/0cad0cdb-0fa0-461c-871e-569b71a4aa64">


<img width="1798" alt="Screenshot 2024-10-23 at 08 43 19" src="https://github.com/user-attachments/assets/74397fe8-b740-4318-a545-269ee4b2337c">


<img width="1731" alt="Screenshot 2024-10-23 at 13 22 39" src="https://github.com/user-attachments/assets/e15f2370-6d12-4902-9389-2ed3353f4511">




Cryptocurrency Dashboard Application
A dashboard built using Dash and Plotly for visualizing and monitoring cryptocurrency market data. This application provides an interactive user interface to track market trends, visualize top gainers, volume trends, ICO information, and more, all in real-time.

Features
- Real-Time Data Updates: The dashboard fetches the latest data from the CoinGecko API to display up-to-date market information and save data to Postgres database, as I have used free API , it has request limits
- Market Overview: A view of the cryptocurrency market, including active cryptocurrencies, and market stats.
- Top Gainers and Trending Coins: Visualizations for the top-performing cryptocurrencies based on market cap and volume.
- Volume and Market Cap Distribution: Graphs showing volume trends and market cap distribution in a pie and bar chart format.
- Interactive Treemap: A treemap to visualize the market cap of various cryptocurrencies.

Technologies
Dash: A Python framework for building analytical web applications.
Plotly: Used for creating interactive graphs and visualizations.
Dash Bootstrap Components: For responsive layouts and styling.
Postgres: A lightweight database used to store and manage cryptocurrency data.
CoinGecko API: For fetching real-time cryptocurrency market data.

Setup and Installation
Clone the Repository:
'git clone https://github.com/your-username/cryptocurrency-dashboard.git
cd cryptocurrency-dashboard'

Create a Virtual Environment:
'python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate'

Install Dependencies:

'pip install -r requirements.txt'

Run the Application:
'python app.py'



