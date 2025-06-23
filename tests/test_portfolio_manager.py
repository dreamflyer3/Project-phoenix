# tests/test_portfolio_manager.py

import unittest
import pandas as pd
from src.data.data_manager import DataManager
from src.risk.risk_manager import RiskManager
from src.strategies.ma_crossover_strategy import MovingAverageCrossoverStrategy
from src.portfolio.portfolio_manager import PortfolioManager

class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        """Create sample data that will generate a profitable 'buy' trade."""
        data = {
            'open':  [100, 102, 104, 106, 108, 115, 120, 125, 130, 135],
            'high':  [101, 103, 105, 107, 109, 116, 121, 126, 131, 136],
            'low':   [99,  101, 103, 105, 107, 114, 119, 124, 129, 134],
            'close': [102, 104, 106, 108, 110, 118, 122, 128, 132, 138],
            'atr':   [2, 2, 2, 2, 2, 3, 3, 3, 3, 3] # Add ATR for risk calculation
        }
        self.sample_data = pd.DataFrame(data)

    def test_backtest_run(self):
        """
        An integration test to ensure the PortfolioManager can run a backtest
        and that the final equity is calculated correctly.
        """
        # --- 1. Setup ---
        initial_capital = 100000.0
        risk_manager = RiskManager()
        strategy = MovingAverageCrossoverStrategy(short_window=3, long_window=6)

        # --- 2. The Test ---
        # Initialize the PortfolioManager
        portfolio_manager = PortfolioManager(
            data=self.sample_data,
            strategy=strategy,
            risk_manager=risk_manager,
            initial_capital=initial_capital
        )

        # Run the backtest
        results = portfolio_manager.run_backtest()
        final_equity = results['equity'].iloc[-1]

        # --- 3. Assertion ---
        # The data is designed to make one profitable trade.
        # Therefore, our final equity should be greater than our starting capital.
        self.assertGreater(final_equity, initial_capital)


if __name__ == '__main__':
    unittest.main()