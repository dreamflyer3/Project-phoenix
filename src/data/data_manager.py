# src/data/data_manager.py

import pandas as pd

class DataManager:
    """
    A simple agent responsible for loading and providing data.
    """
    def load_data(self, file_path):
        """
        Loads data from a given CSV file path.

        Args:
            file_path (str): The full path to the CSV file.

        Returns:
            A pandas DataFrame with the loaded data, or an empty
            DataFrame if the file is not found.
        """
        try:
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            print(f"Error: Data file not found at {file_path}")
            return pd.DataFrame()