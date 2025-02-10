# modules/risk_management.py
from modules.logger import setup_logger
from config import RISK_PER_TRADE, DAILY_LOSS_LIMIT

logger = setup_logger("RiskManagement", log_file="logs/risk_management.log")

class RiskManagement:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_loss = 0.0
        self.RISK_PER_TRADE = RISK_PER_TRADE

    def calculate_order_size(self, buy_price, sell_price):
        spread = sell_price - buy_price
        if spread <= 0:
            logger.error("Non-positive spread; cannot calculate order size.")
            return 0
        risk_amount = self.current_capital * self.RISK_PER_TRADE
        order_size = risk_amount / spread
        logger.debug(f"Spread: {spread}, Risk amount: {risk_amount}, Order size: {order_size}")
        return order_size

    def update_capital(self, pnl):
        self.current_capital += pnl
        if pnl < 0:
            self.daily_loss += abs(pnl)
        logger.info(f"Capital updated: current_capital={self.current_capital}, daily_loss={self.daily_loss}")

    def check_daily_limit(self):
        if self.daily_loss / self.initial_capital > DAILY_LOSS_LIMIT:
            logger.error("Daily loss limit exceeded. Halting trading.")
            return False
        return True

    def set_risk_per_trade(self, new_risk):
        self.RISK_PER_TRADE = new_risk
        logger.info(f"RISK_PER_TRADE updated to: {new_risk}")
