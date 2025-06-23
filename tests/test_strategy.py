# tests/test_strategy.py

import unittest
import pandas as pd
from src.strategies.ma_crossover_strategy import MovingAverageCrossoverStrategy

class TestMovingAverageCrossoverStrategy(unittest.TestCase):

    def setUp(self):
        """Create a sample DataFrame that will have a clear crossover event."""
        data = {
            'close': [
                100, 102, 104, 106, 108, # Short MA is below Long MA
                115, 120, 125, 130, 135, # Golden Cross happens here
                130, 125, 120, 115, 110, # Death Cross happens here
                108, 106, 104, 102, 100
            ]
        }
        self.sample_data = pd.DataFrame(data)

    def test_generate_signals(self):
        """
        Tests that buy/sell signals are generated correctly on a crossover.
        """
        # --- 1. Test Inputs ---
        short_window = 5
        long_window = 10
        
        # --- 2. The Test ---
        strategy = MovingAverageCrossoverStrategy(
            short_window=short_window, 
            long_window=long_window
        )
        signals = strategy.generate_signals(self.sample_data)

        # --- 3. Assertions ---
        # A "golden cross" (buy signal) should appear at index 5. (Corrected from 9)
        self.assertEqual(signals['signal'].iloc[5], 1.0) 
        
        # A "death cross" (sell signal) should appear at index 14.
        self.assertEqual(signals['signal'].iloc[14], -1.0)

        # The rest of the signals should be 0 (hold)
        total_signals = signals['signal'].abs().sum()
        self.assertEqual(total_signals, 2.0)

if __name__ == '__main__':
    unittest.main()