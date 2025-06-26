# tests/test_data_manager.py

import unittest
import os
import pandas as pd
from src.data.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    def test_clean_and_validate_data(self):
        """
        Tests if the DataManager can correctly clean a DataFrame with
        gaps and anomalous data.
        """
        # --- 1. Create "Dirty" Data ---
        # This data has a missing date (Jan 2nd) and a bad row (Jan 4th)
        dirty_data = {
            'timestamp': pd.to_datetime(['2025-01-01', '2025-01-03', '2025-01-04']),
            'open': [100, 105, 115],
            'high': [102, 108, 110], # Note: high is lower than low on Jan 4th
            'low': [99, 104, 112],
            'close': [101, 106, 108],
        }
        dirty_df = pd.DataFrame(dirty_data).set_index('timestamp')

        # --- 2. The Test ---
        data_manager = DataManager()
        # Call the (not-yet-written) cleaning method
        cleaned_df = data_manager.clean_and_validate_data(dirty_df)

        # --- 3. Assertions ---
        # a) Check that the anomalous row (Jan 4th) was dropped
        self.assertEqual(len(cleaned_df), 3)
        self.assertNotIn(pd.to_datetime('2025-01-04'), cleaned_df.index)

        # b) Check that the missing date (Jan 2nd) was added
        self.assertIn(pd.to_datetime('2025-01-02'), cleaned_df.index)

        # c) Check that the values for the new date were forward-filled
        # The values on Jan 2nd should match the values from Jan 1st
        self.assertEqual(cleaned_df.loc['2025-01-02']['close'], 101)

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
            
        # CORRECTED: Added a 'timestamp' column to the dummy data
        dummy_data = {
            'timestamp': ['2025-01-01 00:00:00'],
            'open': [100], 
            'high': [105], 
            'low': [99], 
            'close': [102]
        }
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
        # Call the method to load our dummy data
        loaded_df = data_manager.load_data(self.temp_file_path)

        # --- Assertions ---
        # 1. Check if the result is a pandas DataFrame
        self.assertIsInstance(loaded_df, pd.DataFrame)
        # 2. Check if the DataFrame is not empty
        self.assertFalse(loaded_df.empty)
        # 3. Check if it contains the correct columns (the index_col 'timestamp' is removed)
        self.assertEqual(list(loaded_df.columns), ['open', 'high', 'low', 'close'])


if __name__ == '__main__':
    unittest.main()