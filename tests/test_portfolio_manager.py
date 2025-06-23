# tests/test_portfolio_manager.py

import unittest
import pandas as pd
import numpy as np

# Import all our agents
from src.risk.risk_manager import RiskManager
from src.strategies.ma_crossover_strategy import MovingAverageCrossoverStrategy
from src.portfolio.portfolio_manager import PortfolioManager
from src.regime.regime_filter import RegimeFilter

# --- Dummy Agents for Testing ---
# These simple classes help us create predictable tests.
class BullStrategy: # A strategy that always wants to buy
    def generate_signals(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 1.0
        return signals

class BearStrategy: # A strategy that always wants to sell
    def generate_signals(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = -1.0
        return signals

class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        """Create sample data."""
        data = {
            'open':  [100, 102, 104, 106, 108, 115, 120, 125, 130, 135],
            'high':  [101, 103, 105, 107, 109, 116, 121, 126, 131, 136],
            'low':   [99,  101, 103, 105, 107, 114, 119, 124, 129, 134],
            'close': [102, 104, 106, 108, 110, 118, 122, 128, 132, 138],
            'atr':   [2, 2, 2, 2, 2, 3, 3, 3, 3, 3]
        }
        self.sample_data = pd.DataFrame(data)

    def test_single_strategy_backtest(self):
        """
        Tests a simple backtest with only one strategy.
        This is similar to our old test.
        """
        initial_capital = 100000.0
        risk_manager = RiskManager()
        strategy = MovingAverageCrossoverStrategy(short_window=3, long_window=6)
        
        # We now pass strategies as a dictionary
        strategies = {'default': strategy}

        portfolio_manager = PortfolioManager(
            data=self.sample_data,
            strategies=strategies, # Pass the dictionary
            risk_manager=risk_manager,
            initial_capital=initial_capital
        )

        results = portfolio_manager.run_backtest()
        final_equity = results['equity'].iloc[-1]
        self.assertGreater(final_equity, initial_capital)

    def test_regime_switching_logic(self):
        """
        Tests if the PortfolioManager correctly switches between strategies
        based on the market regime.
        """
        initial_capital = 100000.0
        risk_manager = RiskManager()
        
        # We define a different strategy for each regime
        strategies = {
            'bull': BullStrategy(),
            'bear': BearStrategy()
        }
        
        # We will use a simple regime filter for this test
        regime_filter = RegimeFilter(lookback_period=5)

        portfolio_manager = PortfolioManager(
            data=self.sample_data,
            strategies=strategies,
            risk_manager=risk_manager,
            regime_filter=regime_filter, # Pass in the new agent
            initial_capital=initial_capital
        )
        
        # Run the backtest and get the list of trades taken
        results = portfolio_manager.run_backtest()
        trades = results['trades']

        # The data is always trending up, so the regime should always be 'bull'.
        # Therefore, only the BullStrategy should have been used.
        # We assert that a buy trade was made (trade size > 0)
        self.assertGreater(trades[0]['size'], 0)


if __name__ == '__main__':
    unittest.main()
