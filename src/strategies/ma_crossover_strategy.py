# src/strategies/ma_crossover_strategy.py

import pandas as pd
import numpy as np

class MovingAverageCrossoverStrategy:
    """
    A simple strategy that generates signals based on two moving averages crossing.
    """
    def __init__(self, short_window=5, long_window=10):
        """
        Initializes the strategy with specific window lengths.

        Args:
            short_window (int): The lookback period for the short moving average.
            long_window (int): The lookback period for the long moving average.
        """
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        """
        Generates buy (1), sell (-1), or hold (0) signals.

        Args:
            data (pd.DataFrame): A DataFrame with at least a 'close' column.

        Returns:
            A pandas DataFrame with a 'signal' column.
        """
        # Create a new DataFrame to avoid modifying the original data
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Calculate the short and long moving averages
        signals['short_ma'] = data['close'].rolling(window=self.short_window).mean()
        signals['long_ma'] = data['close'].rolling(window=self.long_window).mean()

        # Create the position state directly in the signals DataFrame to preserve the index
        signals['position'] = np.where(signals['short_ma'] > signals['long_ma'], 1.0, 0.0)
        
        # The signal is the change in state from the previous day
        signals['signal'] = signals['position'].diff()

        return signals