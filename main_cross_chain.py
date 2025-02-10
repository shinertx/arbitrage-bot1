# main_cross_chain.py
import asyncio
import uvloop
uvloop.install()  # Use uvloop for improved performance

from modules.data_feed import DataFeed
from modules.arbitrage_scanner import ArbitrageScanner
from modules.execution_engine import ExecutionEngine
from modules.risk_management import RiskManagement
from modules.cross_chain import CrossChainArbitrage
from modules.logger import setup_logger
from config import TRADING_PAIR

logger = setup_logger("MainCrossChain")

# Set your initial trading capital (e.g., $10K)
INITIAL_CAPITAL = 10000

async def main_loop():
    data_feed = DataFeed()
    scanner = ArbitrageScanner(data_feed)  # Pass data_feed to get volatility data.
    risk_manager = RiskManagement(initial_capital=INITIAL_CAPITAL)
    execution_engine = ExecutionEngine(data_feed.exchanges)
    cross_chain = CrossChainArbitrage()
    token_address = "0xTokenAddressPlaceholder"  # Replace with a real token address when available

    try:
        while True:
            # --- Single-Chain Arbitrage ---
            order_books = await data_feed.get_all_order_books()
            logger.info("Fetched order books from all exchanges.")
            opportunities = scanner.scan(order_books)
            
            if opportunities:
                logger.info(f"Found {len(opportunities)} arbitrage opportunities.")
                for opp in opportunities:
                    logger.info(
                        f"Opportunity: Buy on {opp['buy_exchange']} at {opp['buy_price']} and "
                        f"Sell on {opp['sell_exchange']} at {opp['sell_price']} "
                        f"({opp['profit_percent']:.2f}% profit)"
                    )
                    order_size = risk_manager.calculate_order_size(opp['buy_price'], opp['sell_price'])
                    logger.info(f"Calculated order size: {order_size:.6f}")
                    
                    if not risk_manager.check_daily_limit():
                        logger.error("Daily loss limit reached. Halting trading loop.")
                        return
                    
                    results = await execution_engine.execute_arbitrage(
                        opp['buy_exchange'],
                        opp['sell_exchange'],
                        order_size,
                        opp['buy_price'],
                        opp['sell_price']
                    )
                    logger.info(f"Execution results: {results}")
                    
                    profit = order_size * (opp['sell_price'] - opp['buy_price'])
                    risk_manager.update_capital(profit)
                    logger.info(f"Updated capital: {risk_manager.current_capital:.2f}")
            else:
                logger.info("No single-chain arbitrage opportunities detected at this time.")
            
            # --- Cross-Chain Arbitrage ---
            percent_diff = cross_chain.check_arbitrage(token_address)
            THRESHOLD = 1.0  # Cross-chain arbitrage threshold.
            if percent_diff >= THRESHOLD:
                if cross_chain.get_eth_token_price(token_address) < cross_chain.get_poly_token_price(token_address):
                    logger.info("Cross-chain arbitrage: Bridge from Ethereum to Polygon.")
                    cross_chain.execute_bridge(token_address, amount=1, direction='eth_to_poly')
                else:
                    logger.info("Cross-chain arbitrage: Bridge from Polygon to Ethereum.")
                    cross_chain.execute_bridge(token_address, amount=1, direction='poly_to_eth')
            else:
                logger.info("No cross-chain arbitrage opportunity detected.")
            
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        await data_feed.close_exchanges()

if __name__ == '__main__':
    asyncio.run(main_loop())
