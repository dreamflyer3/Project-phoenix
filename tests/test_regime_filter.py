# tests/test_regime_filter.py

import unittest
import pandas as pd
import numpy as np
from src.regime.regime_filter import RegimeFilter

class TestRegimeFilter(unittest.TestCase):

    def setUp(self):
        """Create sample data for bull and bear regimes."""
        # Data clearly trending upwards
        bull_data = {'close': np.arange(100, 200, 2)} 
        self.bull_market_data = pd.DataFrame(bull_data)

        # Data clearly trending downwards
        bear_data = {'close': np.arange(200, 100, -2)}
        self.bear_market_data = pd.DataFrame(bear_data)

    def test_bull_regime_detection(self):
        """
        Tests if the filter correctly identifies a bull regime (positive slope).
        """
        # --- 1. Setup ---
        # Initialize our (not-yet-written) RegimeFilter agent
        regime_filter = RegimeFilter(lookback_period=20)
        
        # --- 2. The Test ---
        regime = regime_filter.get_regime(self.bull_market_data)
        
        # --- 3. Assertion ---
        # The last detected regime in an uptrend should be 'bull'
        self.assertEqual(regime, 'bull')

    def test_bear_regime_detection(self):
        """
        Tests if the filter correctly identifies a bear regime (negative slope).
        """
        # --- 1. Setup ---
        regime_filter = RegimeFilter(lookback_period=20)

        # --- 2. The Test ---
        regime = regime_filter.get_regime(self.bear_market_data)

        # --- 3. Assertion ---
        # The last detected regime in a downtrend should be 'bear'
        self.assertEqual(regime, 'bear')


if __name__ == '__main__':
    unittest.main()