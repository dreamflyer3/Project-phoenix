# tests/test_data_manager.py

import unittest
import os
import pandas as pd
from src.data.data_manager import DataManager

class TestDataManager(unittest.TestCase):

    def setUp(self):
        """
        This method is run before each test.
        It creates a temporary dummy CSV file for testing.
        """
        self.temp_dir = "temp_test_data"
        self.temp_file_path = os.path.join(self.temp_dir, "dummy_data.csv")
        
        # Create temporary directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        # Create a dummy dataframe and save it to CSV
        dummy_data = {'open': [100], 'high': [105], 'low': [99], 'close': [102]}
        pd.DataFrame(dummy_data).to_csv(self.temp_file_path, index=False)

    def tearDown(self):
        """
        This method is run after each test.
        It cleans up by removing the dummy file and directory.
        """
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_load_csv_data(self):
        """
        Tests if the DataManager can correctly load data from a CSV file.
        """
        # --- The Test ---
        data_manager = DataManager()
        # Call the (not-yet-written) method to load our dummy data
        loaded_df = data_manager.load_data(self.temp_file_path)

        # --- Assertions ---
        # 1. Check if the result is a pandas DataFrame
        self.assertIsInstance(loaded_df, pd.DataFrame)
        # 2. Check if the DataFrame is not empty
        self.assertFalse(loaded_df.empty)
        # 3. Check if it contains the correct columns
        self.assertEqual(list(loaded_df.columns), ['open', 'high', 'low', 'close'])


if __name__ == '__main__':
    unittest.main()