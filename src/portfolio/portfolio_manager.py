# src/portfolio/portfolio_manager.py

import pandas as pd

class PortfolioManager:
    """
    The "CEO" agent responsible for orchestrating the backtest, using all other agents.
    """
    def __init__(self, data, strategy, risk_manager, initial_capital=100000.0):
        """
        Initializes the PortfolioManager.

        Args:
            data (pd.DataFrame): The DataFrame containing market data (OHLC, ATR).
            strategy: The strategy agent to use for generating signals.
            risk_manager: The risk manager agent for position sizing.
            initial_capital (float): The starting capital for the backtest.
        """
        self.data = data
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.initial_capital = initial_capital

    def run_backtest(self):
        """
        Executes the backtest loop.
        """
        # 1. Get signals from the strategy agent
        signals = self.strategy.generate_signals(self.data)

        # 2. Setup portfolio tracking variables
        cash = self.initial_capital
        units_held = 0.0
        equity = [self.initial_capital] # List to track equity over time

        # 3. Loop through each day (each row in our data)
        for i in range(1, len(self.data)):
            current_price = self.data['close'].iloc[i]
            signal = signals['signal'].iloc[i]

            # If we get a BUY signal and are not in a position
            if signal == 1.0 and units_held == 0:
                # Ask the RiskManager how many units to buy
                position_size, stop_loss = self.risk_manager.calculate_trade_parameters(
                    account_balance=cash,
                    risk_percentage=0.02, # This would come from config in a real run
                    entry_price=current_price,
                    atr=self.data['atr'].iloc[i],
                    stop_loss_atr_multiplier=2.0 # Also from config
                )
                
                # Execute the buy
                cash -= position_size * current_price
                units_held = position_size

            # If we get a SELL signal and are in a position
            elif signal == -1.0 and units_held > 0:
                # Execute the sell
                cash += units_held * current_price
                units_held = 0

            # Calculate the current total value of our portfolio
            current_total_equity = cash + (units_held * current_price)
            equity.append(current_total_equity)

        # 4. Create and return the results
        results = pd.DataFrame(index=self.data.index)
        results['equity'] = equity
        return results