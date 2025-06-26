# fetch_data.py

from src.data.data_manager import DataManager

def main():
    """
    Main function to download our baseline historical data.
    """
    data_manager = DataManager()
    
    # --- Configuration ---
    SYMBOL = 'BTC/USDT'
    TIMEFRAME = '1d' # Daily data
    START_DATE = '2018-01-01'
    
    data_manager.fetch_and_save_data(SYMBOL, TIMEFRAME, START_DATE)

if __name__ == "__main__":
    main()