# src/portfolio/portfolio_manager.py

import pandas as pd
import numpy as np

class PortfolioManager:
    """
    Orchestrates the backtest, using all other agents.
    This version includes logic to prevent lookahead bias and to model transaction costs.
    """
    def __init__(self, data, strategies, risk_manager, initial_capital=100000.0, commission_pct=0.0, slippage_pct=0.0, regime_filter=None):
        """
        Initializes the PortfolioManager.

        Args:
            data (pd.DataFrame): DataFrame with market data (OHLC, ATR).
            strategies (dict): Dictionary of strategy agents, keyed by regime name.
            risk_manager: The risk manager agent.
            initial_capital (float): Starting capital for the backtest.
            commission_pct (float): The commission percentage per trade (e.g., 0.001 for 0.1%).
            slippage_pct (float): The slippage percentage per trade (e.g., 0.0005 for 0.05%).
            regime_filter (optional): The regime filter agent.
        """
        self.data = data
        self.strategies = strategies
        self.risk_manager = risk_manager
        self.regime_filter = regime_filter
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct

    def run_backtest(self):
        """
        Executes the backtest loop with realistic trade execution.
        """
        final_signals = self.strategies.get('default')
        if final_signals is None:
            raise ValueError("A 'default' strategy must be provided.")
        final_signals = final_signals.generate_signals(self.data)

        cash = self.initial_capital
        units_held = 0.0
        equity = [self.initial_capital]
        trades = []

        for i in range(1, len(self.data)):
            signal = final_signals['signal'].iloc[i-1]
            market_price = self.data['open'].iloc[i]

            # If we get a BUY signal and are not in a position
            if signal == 1.0 and units_held == 0:
                # SLIPPAGE: We pay a little more than the market price
                slipped_buy_price = market_price * (1 + self.slippage_pct)

                position_size, stop_loss = self.risk_manager.calculate_trade_parameters(
                    account_balance=cash, risk_percentage=0.02, entry_price=market_price, # Sizing is based on market price
                    atr=self.data['atr'].iloc[i-1], stop_loss_atr_multiplier=2.0
                )
                
                if position_size > 0:
                    trade_value = position_size * slipped_buy_price
                    commission = trade_value * self.commission_pct
                    
                    if cash >= (trade_value + commission):
                        cash -= (trade_value + commission)
                        units_held = position_size
                        trades.append({'type': 'buy', 'price': slipped_buy_price, 'size': units_held})

            # If we get a SELL signal and are in a position
            elif signal == -1.0 and units_held > 0:
                # SLIPPAGE: We receive a little less than the market price
                slipped_sell_price = market_price * (1 - self.slippage_pct)

                trade_value = units_held * slipped_sell_price
                commission = trade_value * self.commission_pct
                
                cash += (trade_value - commission)
                trades.append({'type': 'sell', 'price': slipped_sell_price, 'size': units_held})
                units_held = 0

            current_total_equity = cash + (units_held * self.data['close'].iloc[i])
            equity.append(current_total_equity)

        results = pd.DataFrame(index=self.data.index)
        results['equity'] = equity
        results['trades'] = pd.Series(trades)
        return results