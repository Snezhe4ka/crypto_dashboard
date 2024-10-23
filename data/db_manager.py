from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import json


USERNAME = 'sni'
PASSWORD = ''
HOST = 'localhost'
PORT = '5432'
DB_NAME = 'crypto_data'
DB_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

Base = declarative_base()

# Define the engine and session
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


class MarketData(Base):
    __tablename__ = 'market_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    name = Column(String)
    image = Column(String)
    current_price = Column(Float)
    market_cap = Column(Float)
    market_cap_rank = Column(Integer)
    fully_diluted_valuation = Column(Float)
    total_volume = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    price_change_24h = Column(Float)
    price_change_percentage_24h = Column(Float)
    market_cap_change_24h = Column(Float)
    market_cap_change_percentage_24h = Column(Float)
    circulating_supply = Column(Float)
    total_supply = Column(Float)
    max_supply = Column(Float)
    ath = Column(Float)
    ath_change_percentage = Column(Float)
    ath_date = Column(DateTime)
    atl = Column(Float)
    atl_change_percentage = Column(Float)
    atl_date = Column(DateTime)
    roi = Column(JSON, nullable=True)
    last_updated = Column(DateTime)
    price_change_percentage_1h = Column(Float, nullable=True)
    sparkline_in_7d = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class GlobalData(Base):
    __tablename__ = 'global_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    active_cryptocurrencies = Column(Integer)
    upcoming_icos = Column(Integer)
    ongoing_icos = Column(Integer)
    ended_icos = Column(Integer)
    markets = Column(Integer)
    total_market_cap = Column(JSON)
    total_volume = Column(JSON)
    market_cap_percentage = Column(JSON)
    market_cap_change_percentage_24h_usd = Column(Float)
    updated_at = Column(DateTime)
    timestamp = Column(DateTime, default=datetime.utcnow)


class MarketDominance(Base):
    __tablename__ = 'market_dominance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    btc = Column(Float)
    eth = Column(Float)
    usdt = Column(Float)
    usdc = Column(Float)
    bnb = Column(Float)
    sol = Column(Float)
    xrp = Column(Float)
    others = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class TrendingCoins(Base):
    __tablename__ = 'trending_coins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String)
    coin_name = Column(String)
    symbol = Column(String)
    market_cap_rank = Column(Integer)
    small = Column(String)
    score = Column(Float)
    price = Column(Float)
    market_cap = Column(String)
    total_volume = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(String)
    name = Column(String)
    market_cap = Column(Float)
    market_cap_24h_change = Column(Float)
    top_3_coins = Column(JSON)
    volume_24h = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class TopGainersMarketCap(Base):
    __tablename__ = 'top_gainers_market_cap'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    symbol = Column(String)
    price = Column(Float)
    change_24h = Column(Float)
    percent_change_7d = Column(Float)
    market_cap_change_percentage_24h = Column(Float)
    market_cap = Column(Float)
    market_cap_dominance = Column(Float)
    date_added = Column(DateTime)  # Changed to DateTime
    data_period = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class TopProjectsByVolume(Base):
    __tablename__ = 'top_projects_by_volume'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    symbol = Column(String)
    total_volume = Column(Float)
    market_cap = Column(Float)
    last_updated = Column(DateTime)
    timestamp = Column(DateTime, default=datetime.utcnow)


def initialize_db():
    print("Creating tables if they do not exist...")
    Base.metadata.create_all(bind=engine)


# initialize the database
initialize_db()


# insert data functions
def insert_market_data(market_data):
    session = SessionLocal()
    try:
        # clear existing data before inserting
        session.query(MarketData).delete()
        session.commit()

        market_data_objects = [MarketData(**{key: coin[key] for key in coin if key != 'id'}) for coin in market_data]
        session.add_all(market_data_objects)
        session.commit()
        print("Market Data Inserted Successfully")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting market data: {e}")
    finally:
        session.close()


def insert_global_data(data):
    session = SessionLocal()
    try:
        session.query(GlobalData).delete()
        session.commit()

        global_data_obj = GlobalData(**data)
        session.add(global_data_obj)
        session.commit()
        print("Global Data Inserted Successfully")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting global data: {e}")
    finally:
        session.close()


def insert_market_dominance(data):
    session = SessionLocal()
    try:
        session.query(MarketDominance).delete()
        session.commit()

        market_dominance_object = MarketDominance(**data)

        session.add(market_dominance_object)
        session.commit()
        print("Market Dominance Inserted Successfully")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting market dominance: {e}")
    finally:
        session.close()


def insert_trending_coins(data):
    session = SessionLocal()
    try:
        session.query(TrendingCoins).delete()
        session.commit()

        # filter the data to match the columns in TrendingCoins
        filtered_trending_coins = [
            {
                key: value for key, value in coin.items()
                if key in TrendingCoins.__table__.columns.keys()
            }
            for coin in data
        ]

        # create objects for each trending coin
        trending_coin_objects = [TrendingCoins(**coin) for coin in filtered_trending_coins]

        session.add_all(trending_coin_objects)
        session.commit()
        print("Trending Coins Inserted Successfully")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting trending coins: {e}")
    finally:
        session.close()


def insert_category_data(data):
    session = SessionLocal()
    try:
        # clear existing data before inserting
        session.query(Categories).delete()
        session.commit()

        category_objects = [Categories(**category) for category in data]
        session.add_all(category_objects)
        session.commit()
        print("Category Data Inserted Successfully")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting category data: {e}")
    finally:
        session.close()


def insert_top_gainers_market_cap():
    session = SessionLocal()
    try:

        # top 10 gainers by market cap change percentage in the last 24 hours
        top_gainers = session.query(MarketData).order_by(MarketData.market_cap_change_percentage_24h.desc()).limit(20).all()

        # clear existing data before inserting
        session.query(TopGainersMarketCap).delete()
        session.commit()

        # data for insertion
        top_gainers_data = [
            TopGainersMarketCap(
                name=gainer.name,
                symbol=gainer.symbol,
                price=gainer.current_price,
                change_24h=gainer.price_change_24h,
                percent_change_7d=gainer.price_change_percentage_1h,  # Assuming this is intended; change if needed
                market_cap_change_percentage_24h=gainer.market_cap_change_percentage_24h,
                market_cap=gainer.market_cap,
                market_cap_dominance=None,  # Set if you have this value in MarketData
                date_added=gainer.last_updated,  # Assuming `last_updated` is equivalent to `date_added`
                data_period="24h",  # Assuming you want to set this as "24h"; adjust as necessary
                timestamp=datetime.utcnow()
            )
            for gainer in top_gainers
        ]

        session.add_all(top_gainers_data)
        session.commit()
        print("Top Gainers by Market Cap Inserted Successfully")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting top gainers by market cap: {e}")
    finally:
        session.close()


def insert_top_projects_by_volume():
    session = SessionLocal()
    try:
        # top 10 projects by total volume in the last 24 hours
        top_volume_projects = session.query(MarketData).order_by(MarketData.total_volume.desc()).limit(20).all()

        # clear existing data before inserting
        session.query(TopProjectsByVolume).delete()
        session.commit()

        # data for insertion
        top_volume_data = [
            TopProjectsByVolume(
                name=project.name,
                symbol=project.symbol,
                total_volume=project.total_volume,
                market_cap=project.market_cap,
                last_updated=project.last_updated,
                timestamp=datetime.utcnow()
            )
            for project in top_volume_projects
        ]

        session.add_all(top_volume_data)
        session.commit()
        print("Top Projects by Volume Inserted Successfully")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting top projects by volume: {e}")
    finally:
        session.close()



