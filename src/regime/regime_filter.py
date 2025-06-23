# src/regime/regime_filter.py

import pandas as pd
import numpy as np

class RegimeFilter:
    """
    A simple agent to determine the market regime (e.g., bull or bear)
    based on the slope of a moving average.
    """
    def __init__(self, lookback_period=200):
        """
        Initializes the filter with a specific lookback period for the moving average.

        Args:
            lookback_period (int): The number of periods for the moving average.
        """
        self.lookback_period = lookback_period

    def get_regime(self, data):
        """
        Determines the current market regime from the provided data.

        Args:
            data (pd.DataFrame): A DataFrame with at least a 'close' column.

        Returns:
            str: The determined regime, e.g., 'bull' or 'bear'.
        """
        # 1. Calculate the moving average
        ma = data['close'].rolling(window=self.lookback_period).mean()

        # 2. Get the most recent data points of the moving average to calculate the slope
        # We need at least 2 points to determine a slope.
        recent_ma = ma.dropna()[-self.lookback_period:]
        if len(recent_ma) < 2:
            return 'neutral' # Not enough data to determine a regime

        # 3. Use numpy's polyfit to find the slope of the line that best fits the recent MA points
        # The first element (m) of the returned array [m, c] is the slope.
        slope = np.polyfit(range(len(recent_ma)), recent_ma, 1)[0]
        
        # 4. Classify the regime based on the slope
        if slope > 0:
            return 'bull'
        else:
            return 'bear'