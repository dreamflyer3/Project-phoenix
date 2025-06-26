# src/strategies/asymmetrical_ema_strategy.py

import pandas as pd
import numpy as np

class AsymmetricalEmaStrategy:
    """
    A strategy that uses a fast EMA crossover for entry, but a slow,
    regime-based signal for exiting to hold trends longer.
    """
    def __init__(self, short_ema=21, long_ema=55, regime_ma=200):
        self.short_ema = short_ema
        self.long_ema = long_ema
        self.regime_ma = regime_ma

    def generate_signals(self, data):
        """Generates the final buy/sell signals."""
        
        # --- Entry Logic ---
        ema_short = data['close'].ewm(span=self.short_ema, adjust=False).mean()
        ema_long = data['close'].ewm(span=self.long_ema, adjust=False).mean()
        
        # --- Exit Logic ---
        regime_ma = data['close'].rolling(window=self.regime_ma).mean()
        regime_slope = regime_ma.rolling(window=30).apply(lambda x: np.polyfit(range(30), x, 1)[0], raw=False)
        
        # --- Position Logic ---
        position = pd.Series(index=data.index, dtype=float)
        
        # Set a buy trigger
        buy_trigger = (ema_short > ema_long) & (ema_short.shift(1) <= ema_long.shift(1))
        position[buy_trigger] = 1.0
        
        # Set an exit trigger
        exit_trigger = (regime_slope < 0)
        position[exit_trigger] = 0.0
        
        # Forward-fill the position to hold the trade
        position.ffill(inplace=True)
        position.fillna(0, inplace=True)
        
        # Determine final trades
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = position.diff()
        
        return signals
    