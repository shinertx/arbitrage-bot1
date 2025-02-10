# modules/execution_engine.py
import asyncio
import ccxt.async_support as ccxt
from modules.logger import setup_logger
from config import TRADING_PAIR, SLIPPAGE_PERCENTAGE

logger = setup_logger("ExecutionEngine", log_file="logs/execution_engine.log")

class ExecutionEngine:
    def __init__(self, exchanges):
        self.exchanges = exchanges

    async def place_order(self, exchange, order_type, side, amount, price=None, retries=3, delay=1):
        for attempt in range(retries):
            try:
                adjusted_price = price
                if price is not None:
                    if side == 'buy':
                        adjusted_price = price * (1 + SLIPPAGE_PERCENTAGE)
                    elif side == 'sell':
                        adjusted_price = price * (1 - SLIPPAGE_PERCENTAGE)
                    logger.debug(f"Adjusted {side} price on {exchange.name}: {adjusted_price}")
                if order_type == 'limit':
                    order = await exchange.create_order(TRADING_PAIR, order_type, side, amount, adjusted_price)
                elif order_type == 'market':
                    order = await exchange.create_order(TRADING_PAIR, order_type, side, amount)
                else:
                    raise ValueError("Unsupported order type")
                logger.info(f"Placed {side} order on {exchange.name}: {order}")
                return order
            except Exception as e:
                logger.error(f"Error placing {side} order on {exchange.name} (attempt {attempt+1}): {e}")
                await asyncio.sleep(delay)
        return None

    async def execute_arbitrage(self, buy_exchange_name, sell_exchange_name, amount, buy_price, sell_price):
        buy_exchange = self.exchanges.get(buy_exchange_name)
        sell_exchange = self.exchanges.get(sell_exchange_name)
        if not buy_exchange or not sell_exchange:
            logger.error("One or both exchanges not found for execution")
            return None

        tasks = [
            self.place_order(buy_exchange, 'limit', 'buy', amount, buy_price),
            self.place_order(sell_exchange, 'limit', 'sell', amount, sell_price)
        ]
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                logger.error(f"Error in one side of arbitrage: {e}")
                results.append(None)
        return results
