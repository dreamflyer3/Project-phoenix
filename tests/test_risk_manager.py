# tests/test_risk_manager.py

import unittest
import configparser
from src.risk.risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):

    def test_calculate_position_size_and_sl(self):
        """
        Tests the core logic for calculating position size and stop-loss
        based on parameters from the config file.
        """
        # --- 1. Load Settings from Config File ---
        config = configparser.ConfigParser()
        config.read('config.ini')

        risk_percentage = config.getfloat('Risk', 'risk_percentage')
        stop_loss_atr_multiplier = config.getfloat('Risk', 'stop_loss_atr_multiplier')

        # --- 2. Test Inputs ---
        account_balance = 100000.0
        entry_price = 50000.0
        atr = 1500.0
        
        # --- 3. Expected Outputs (Calculated using config settings) ---
        expected_risk_amount = account_balance * risk_percentage
        expected_stop_loss_price = entry_price - (atr * stop_loss_atr_multiplier)
        risk_per_unit = entry_price - expected_stop_loss_price
        expected_position_size = expected_risk_amount / risk_per_unit

        # --- 4. The Test ---
        risk_manager = RiskManager()
        actual_position_size, actual_stop_loss_price = risk_manager.calculate_trade_parameters(
            account_balance=account_balance,
            risk_percentage=risk_percentage,
            entry_price=entry_price,
            atr=atr,
            stop_loss_atr_multiplier=stop_loss_atr_multiplier
        )

        # --- 5. Assertions ---
        self.assertAlmostEqual(actual_position_size, expected_position_size, places=7)
        self.assertAlmostEqual(actual_stop_loss_price, expected_stop_loss_price, places=7)


if __name__ == '__main__':
    unittest.main()