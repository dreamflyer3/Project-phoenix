# src/portfolio/portfolio_manager.py

import pandas as pd
import numpy as np

class PortfolioManager:
    """
    The "CEO" agent responsible for orchestrating the backtest, using all other agents.
    """
    def __init__(self, data, strategies, risk_manager, initial_capital=100000.0, regime_filter=None):
        """
        Initializes the PortfolioManager.

        Args:
            data (pd.DataFrame): The DataFrame containing market data (OHLC, ATR).
            strategies (dict): A dictionary of strategy agents, keyed by regime name (e.g., 'bull', 'bear').
            risk_manager: The risk manager agent for position sizing.
            initial_capital (float): The starting capital for the backtest.
            regime_filter (optional): The regime filter agent. Defaults to None.
        """
        self.data = data
        self.strategies = strategies
        self.risk_manager = risk_manager
        self.regime_filter = regime_filter
        self.initial_capital = initial_capital

    def run_backtest(self):
        """
        Executes the backtest loop with regime-switching logic.
        """
        # 1. Generate all signals first
        all_signals = {name: strategy.generate_signals(self.data) for name, strategy in self.strategies.items()}

        # 2. Determine the regime for each day
        if self.regime_filter:
            # Note: A real implementation would get a regime for each day.
            # For this test, we simplify by getting one regime for the whole dataset.
            current_regime = self.regime_filter.get_regime(self.data)
        else:
            current_regime = 'default' # Use the 'default' strategy if no filter is provided

        # 3. Select the final signals based on the regime
        # If the determined regime has a dedicated strategy, use it. Otherwise, use the default.
        final_signals = all_signals.get(current_regime, all_signals.get('default'))

        if final_signals is None:
            raise ValueError("No applicable or default strategy found for the current regime.")
            
        # 4. Setup portfolio tracking variables
        cash = self.initial_capital
        units_held = 0.0
        equity = [self.initial_capital]
        trades = [] # To log our trades

        # 5. Loop through each day
        for i in range(1, len(self.data)):
            current_price = self.data['close'].iloc[i]
            signal = final_signals['signal'].iloc[i]

            # If we get a BUY signal and are not in a position
            if signal == 1.0 and units_held == 0:
                position_size, stop_loss = self.risk_manager.calculate_trade_parameters(
                    account_balance=cash, risk_percentage=0.02, entry_price=current_price,
                    atr=self.data['atr'].iloc[i], stop_loss_atr_multiplier=2.0
                )
                if position_size > 0:
                    cash -= position_size * current_price
                    units_held = position_size
                    trades.append({'type': 'buy', 'price': current_price, 'size': units_held})

            # If we get a SELL signal and are in a position
            elif signal == -1.0 and units_held > 0:
                cash += units_held * current_price
                trades.append({'type': 'sell', 'price': current_price, 'size': units_held})
                units_held = 0

            current_total_equity = cash + (units_held * current_price)
            equity.append(current_total_equity)

        # 6. Create and return the results
        results = pd.DataFrame(index=self.data.index)
        results['equity'] = equity
        results['trades'] = pd.Series(trades) # Store the list of trades
        return results