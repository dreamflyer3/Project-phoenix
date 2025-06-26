# src/data/data_manager.py

import pandas as pd
import ccxt
import os
from datetime import datetime

class DataManager:
    """
    An agent responsible for fetching, loading, and providing data.
    """
    def clean_and_validate_data(self, df):
        """
        Cleans and validates the raw market data.
        - Removes rows with impossible OHLC values.
        - Fills gaps in the timeline using forward-fill.

        Args:
            df (pd.DataFrame): The raw DataFrame with a DatetimeIndex.

        Returns:
            A cleaned and validated pandas DataFrame.
        """
        # 1. Validate OHLC data: drop rows where low > high
        invalid_rows = df[df['low'] > df['high']]
        if not invalid_rows.empty:
            print(f"Warning: Found and dropped {len(invalid_rows)} rows with impossible OHLC data.")
            df = df.drop(invalid_rows.index)

        # 2. Fill gaps in the timeline
        # Create a complete daily date range from the first to the last day
        full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        
        # Reindex the dataframe to this full range. Missing dates will have NaN values.
        df = df.reindex(full_date_range)
        
        # Use forward-fill to populate NaN values for missing days
        df.ffill(inplace=True)
        
        # It's possible the very first rows are still NaN if the gap was at the start
        df.dropna(inplace=True)

        return df
    
    def fetch_and_save_data(self, symbol, timeframe, start_date_str, data_dir='data'):
        """
        Fetches historical OHLCV data from Binance and saves it to a CSV file.

        Args:
            symbol (str): The symbol to fetch (e.g., 'BTC/USDT').
            timeframe (str): The timeframe (e.g., '1d', '4h').
            start_date_str (str): The start date in 'YYYY-MM-DD' format.
            data_dir (str): The directory to save the data in.
        """
        print(f"Fetching {symbol} {timeframe} data from {start_date_str}...")
        exchange = ccxt.binance()
        
        # Convert the start date string to milliseconds for the API
        since = exchange.parse8601(f'{start_date_str}T00:00:00Z')
        
        all_ohlcv = []
        while True:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            if len(ohlcv) == 0:
                break
            all_ohlcv += ohlcv
            since = ohlcv[-1][0] + 1 # Move to the next timestamp
            print(f"  Fetched {len(ohlcv)} candles, continuing from {exchange.iso8601(since)}")

        # Convert to a pandas DataFrame
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Save to file
        file_path = os.path.join(data_dir, f"{symbol.replace('/', '_')}_{timeframe}.csv")
        df.to_csv(file_path)
        print(f"\nData successfully saved to {file_path}")
        return file_path

    def load_data(self, file_path):
        """
        Loads data from a given CSV file path.
        """
        try:
            df = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
            return df
        except FileNotFoundError:
            print(f"Error: Data file not found at {file_path}")
            return pd.DataFrame()