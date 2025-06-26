# tests/test_portfolio_manager.py

import unittest
import pandas as pd
import numpy as np

# Import all our agents
from src.risk.risk_manager import RiskManager
from src.strategies.ma_crossover_strategy import MovingAverageCrossoverStrategy
from src.portfolio.portfolio_manager import PortfolioManager

class TestPortfolioManager(unittest.TestCase):

    def setUp(self):
        """
        Create sample data where a buy signal on day 4 should trigger a
        trade on day 5's open price.
        """
        data = {
            'open':  [100, 101, 102, 103, 107, 108, 109, 110],
            'high':  [101, 102, 103, 104, 108, 109, 110, 111],
            'low':   [99,  100, 101, 102, 106, 107, 108, 109],
            'close': [101, 102, 103, 106, 107, 108, 109, 110], # Cross happens on day 3's close
            'atr':   [2, 2, 2, 2, 2, 2, 2, 2]
        }
        self.sample_data = pd.DataFrame(data)

    def test_backtest_with_all_costs(self):
        """
        Tests if the backtester correctly applies commission and slippage
        and executes trades on the next bar's open.
        """
        # --- 1. Setup ---
        initial_capital = 100000.0
        commission_pct = 0.001  # 0.1% commission
        slippage_pct = 0.0005 # 0.05% slippage

        risk_manager = RiskManager()
        strategy = MovingAverageCrossoverStrategy(short_window=2, long_window=4)
        strategies = {'default': strategy}

        # --- 2. Manual Calculation for Verification ---
        # Signal on day 3 (close 106), execute on day 4 (open 107).
        market_entry_price = 107.0
        # Account for slippage on the buy order (we pay more)
        slipped_entry_price = market_entry_price * (1 + slippage_pct) # 107 * 1.0005 = 107.0535

        # Position size is calculated based on market prices, not slipped prices.
        risk_per_trade = initial_capital * 0.02
        atr_on_trade_day = 2.0
        stop_loss_price = market_entry_price - (atr_on_trade_day * 2.0) # 107 - 4 = 103
        risk_per_unit = market_entry_price - stop_loss_price # 107 - 103 = 4.0
        position_size = risk_per_trade / risk_per_unit # 2000 / 4 = 500 units
        
        # Calculate final costs using the slipped price
        trade_value = position_size * slipped_entry_price # 500 * 107.0535 = 53526.75
        commission = trade_value * commission_pct # 53526.75 * 0.001 = 53.53
        
        cash_after_buy = initial_capital - trade_value - commission
        
        final_holding_value = position_size * 110.0 # End price is 110
        expected_final_equity = cash_after_buy + final_holding_value # (100k-53526.75-53.53) + 55k = 91419.72

        # --- 3. The Test ---
        portfolio_manager = PortfolioManager(
            data=self.sample_data,
            strategies=strategies,
            risk_manager=risk_manager,
            initial_capital=initial_capital,
            commission_pct=commission_pct,
            slippage_pct=slippage_pct # Pass in the new slippage parameter
        )
        results = portfolio_manager.run_backtest()
        final_equity = results['equity'].iloc[-1]

        # --- 4. Assertion ---
        self.assertAlmostEqual(final_equity, expected_final_equity, places=2)


if __name__ == '__main__':
    unittest.main()