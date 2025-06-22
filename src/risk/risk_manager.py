# src/risk/risk_manager.py

class RiskManager:
    """
    A simple agent responsible for all risk management calculations.
    """
    def calculate_trade_parameters(self, account_balance, risk_percentage, entry_price, atr, stop_loss_atr_multiplier):
        """
        Calculates the position size and stop-loss price for a trade.

        Returns:
            A tuple containing (position_size, stop_loss_price).
            Returns (0, 0) if risk cannot be calculated (e.g., division by zero).
        """
        # Calculate the total dollar amount to risk on this single trade
        risk_amount_usd = account_balance * risk_percentage

        # Calculate the stop-loss price based on volatility (ATR)
        stop_loss_price = entry_price - (atr * stop_loss_atr_multiplier)

        # Calculate the risk per unit of the asset
        risk_per_unit = entry_price - stop_loss_price

        # Avoid division by zero if entry price equals the stop-loss price
        if risk_per_unit <= 0:
            return 0, 0

        # Calculate the number of units to buy/sell
        position_size = risk_amount_usd / risk_per_unit

        return position_size, stop_loss_price