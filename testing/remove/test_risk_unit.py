import unittest
from unittest.mock import MagicMock
from bitmango_free.exchange.risk_manager import RiskManager

class TestRiskManagerUnit(unittest.TestCase):
    def test_permission_safety(self):
        print("Testing RiskManager: Permission Safety...")
        
        # 1. Read-Only Permissions (Should PASS)
        mock_exchange = MagicMock()
        mock_exchange.info = {"permissions": {"read": True, "trade": False, "withdraw": False}}
        self.assertTrue(RiskManager.check_api_permissions(mock_exchange))
        print("  Read-Only: PASS ✓")

        # 2. Trade Permissions (Should PASS)
        mock_exchange.info = {"permissions": {"read": True, "trade": True, "withdraw": False}}
        self.assertTrue(RiskManager.check_api_permissions(mock_exchange))
        print("  Trade-Only: PASS ✓")

        # 3. Withdrawal Permissions (Should FAIL)
        mock_exchange.info = {"permissions": {"read": True, "trade": True, "withdraw": True}}
        with self.assertRaises(ValueError) as cm:
            RiskManager.check_api_permissions(mock_exchange)
        self.assertIn("SECURITY BREACH", str(cm.exception))
        print("  Withdraw-Enabled: REJECTED ✓")

        # 4. Transfer Permissions (Should FAIL)
        mock_exchange.info = {"perm": ["spot", "margin", "transfer"]}
        with self.assertRaises(ValueError) as cm:
            RiskManager.check_api_permissions(mock_exchange)
        self.assertIn("SECURITY BREACH", str(cm.exception))
        print("  Transfer-Enabled: REJECTED ✓")

    def test_notional_calculation(self):
        print("\nTesting RiskManager: Notional Calculation & Caps...")
        
        mock_exchange = MagicMock()
        # Mock price fetching for various assets
        # BTC price = 70,000, ETH price = 2,500
        mock_exchange._fetch_current_price.side_effect = lambda sym, buy: 70000.0 if "BTC" in sym else 2500.0
        
        # 1. 0.1 BTC ($7,000) - Should PASS (Cap is $10k)
        self.assertTrue(RiskManager.validate_order(mock_exchange, "BTC/USDT", "market", "buy", 0.1))
        print("  0.1 BTC ($7,000): PASS ✓")

        # 2. 0.2 BTC ($14,000) - Should FAIL
        with self.assertRaises(ValueError) as cm:
            RiskManager.validate_order(mock_exchange, "BTC/USDT", "market", "buy", 0.2)
        self.assertIn("RISK BREACH", str(cm.exception))
        print("  0.2 BTC ($14,000): REJECTED ✓")

        # 3. 3 ETH ($7,500) - Should PASS
        self.assertTrue(RiskManager.validate_order(mock_exchange, "ETH/USDT", "market", "buy", 3.0))
        print("  3 ETH ($7,500): PASS ✓")

        # 4. 5 ETH ($12,500) - Should FAIL
        with self.assertRaises(ValueError) as cm:
            RiskManager.validate_order(mock_exchange, "ETH/USDT", "market", "buy", 5.0)
        self.assertIn("RISK BREACH", str(cm.exception))
        print("  5 ETH ($12,500): REJECTED ✓")

if __name__ == "__main__":
    unittest.main()
