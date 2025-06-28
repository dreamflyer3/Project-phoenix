# src/data/data_manager.py

import pandas as pd
import ccxt
import os
from datetime import datetime
import requests
import numpy as np

class DataManager:
    """
    An agent responsible for fetching, loading, and cleaning data from various sources.
    """
    def fetch_and_save_data(self, symbol, timeframe, start_date_str, data_dir='data'):
        """
        Fetches historical OHLCV data from an exchange and saves it to a CSV file.
        """
        print(f"Fetching {symbol} {timeframe} data from {start_date_str}...")
        exchange = ccxt.kraken() # Using Kraken as our reliable source

        since = exchange.parse8601(f'{start_date_str}T00:00:00Z')

        all_ohlcv = []
        while True:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            if len(ohlcv) == 0:
                break
            all_ohlcv += ohlcv
            since = ohlcv[-1][0] + 1
            print(f"  Fetched {len(ohlcv)} candles, continuing from {exchange.iso8601(since)}")

        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        file_path = os.path.join(data_dir, f"{symbol.replace('/', '_')}_{timeframe}.csv")
        df.to_csv(file_path)
        print(f"\nData successfully saved to {file_path}")
        return file_path

    def fetch_fear_and_greed_index(self, data_dir='data'):
        """
        Fetches historical Fear & Greed Index data from alternative.me's API.
        """
        print("Fetching historical Fear & Greed Index data...")
        url = "https://api.alternative.me/fng/?limit=0"

        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()['data']
            df = pd.DataFrame(json_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            df['value'] = pd.to_numeric(df['value'])
            df = df[['value', 'value_classification']]

            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            file_path = os.path.join(data_dir, "btc_fear_greed_daily.csv")
            df.to_csv(file_path)

            print(f"Fear & Greed Index data successfully saved to {file_path}")
            return file_path

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return None

    def load_data(self, file_path, index_col='timestamp'):
        """
        Loads data from a given CSV file path.
        """
        try:
            df = pd.read_csv(file_path, index_col=index_col, parse_dates=True)
            return df
        except FileNotFoundError:
            print(f"Error: Data file not found at {file_path}")
            return pd.DataFrame()
        except ValueError:
            print(f"Error: Column '{index_col}' not found in {file_path}. Please check the CSV.")
            return pd.DataFrame()

    def clean_and_validate_data(self, df):
        """
        Cleans and validates the raw market data.
        """
        # 1. Validate OHLC data: drop rows where low > high
        invalid_rows = df[df['low'] > df['high']]
        if not invalid_rows.empty:
            print(f"Warning: Found and dropped {len(invalid_rows)} rows with impossible OHLC data.")
            df = df.drop(invalid_rows.index)

        # 2. Fill gaps in the timeline
        full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        df = df.reindex(full_date_range)
        df.ffill(inplace=True)
        df.dropna(inplace=True)

        return df