# src/strategies/sopr_ema_strategy.py

import pandas as pd
import numpy as np

class SoprEmaStrategy:
    """
    The final strategy:
    - FILTER: Only considers buying after an on-chain capitulation event (SOPR < 1).
    - ENTRY: Buys on a fast EMA crossover.
    - EXIT: Sells on a slow, long-term regime change.
    """
    def __init__(self, short_ema=21, long_ema=55, regime_ma=200, sopr_threshold=1.0):
        self.short_ema = short_ema
        self.long_ema = long_ema
        self.regime_ma = regime_ma
        self.sopr_threshold = sopr_threshold

    def generate_signals(self, data):
        """Generates the final buy/sell signals."""
        
        # --- Calculate all necessary indicators ---
        data['ema_short'] = data['close'].ewm(span=self.short_ema, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=self.long_ema, adjust=False).mean()
        
        regime_ma = data['close'].rolling(window=self.regime_ma).mean()
        regime_slope = regime_ma.rolling(window=30).apply(lambda x: np.polyfit(range(30), x, 1)[0], raw=False)
        
        # --- Define Conditions ---
        # Condition 1: The market must have recently been in capitulation (SOPR < 1)
        # We create a rolling window to see if SOPR has been below 1 in the last 30 days
        is_armed = (data['sopr'].rolling(window=30).min() < self.sopr_threshold)
        
        # Condition 2: The medium-term trend must turn bullish
        is_ema_cross_buy = (data['ema_short'] > data['ema_long']) & (data['ema_short'].shift(1) <= data['ema_long'].shift(1))
        
        # Condition 3: The long-term trend must be bullish for us to hold
        is_bull_regime = (regime_slope > 0)
        
        # --- Position Logic ---
        position = pd.Series(index=data.index, dtype=float)
        
        # Set buy trigger when armed AND the EMA cross happens
        buy_trigger = is_armed & is_ema_cross_buy
        position[buy_trigger] = 1.0
        
        # Set exit trigger when the regime flips to bear
        position[~is_bull_regime] = 0.0
        
        position.ffill(inplace=True)
        position.fillna(0, inplace=True)
        
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = position.diff()
        
        return signals