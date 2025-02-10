# modules/arbitrage_scanner.py
from modules.logger import setup_logger
from config import BASE_MIN_PROFIT_THRESHOLD, VOLATILITY_MULTIPLIER

logger = setup_logger("ArbitrageScanner", log_file="logs/arbitrage_scanner.log")

class ArbitrageScanner:
    def __init__(self, data_feed):
        self.data_feed = data_feed

    def scan(self, order_books):
        opportunities = []
        exchanges = list(order_books.keys())
        for i in range(len(exchanges)):
            volatility = self.data_feed.get_volatility(exchanges[i])
            adjusted_threshold = BASE_MIN_PROFIT_THRESHOLD + (volatility * VOLATILITY_MULTIPLIER)
            logger.info(f"Volatility for {exchanges[i]}: {volatility:.4f}, Adjusted Threshold: {adjusted_threshold:.4f}%")
            for j in range(i + 1, len(exchanges)):
                ex_a, ex_b = exchanges[i], exchanges[j]
                book_a, book_b = order_books[ex_a], order_books[ex_b]
                if not book_a or not book_b:
                    continue

                best_ask_a = book_a['asks'][0][0] if book_a.get('asks') else None
                best_bid_a = book_a['bids'][0][0] if book_a.get('bids') else None
                best_ask_b = book_b['asks'][0][0] if book_b.get('asks') else None
                best_bid_b = book_b['bids'][0][0] if book_b.get('bids') else None

                if best_ask_a and best_bid_b:
                    profit_percent = ((best_bid_b - best_ask_a) / best_ask_a) * 100
                    if profit_percent >= adjusted_threshold:
                        opportunities.append({
                            'buy_exchange': ex_a,
                            'sell_exchange': ex_b,
                            'buy_price': best_ask_a,
                            'sell_price': best_bid_b,
                            'profit_percent': profit_percent
                        })
                if best_ask_b and best_bid_a:
                    profit_percent = ((best_bid_a - best_ask_b) / best_ask_b) * 100
                    if profit_percent >= adjusted_threshold:
                        opportunities.append({
                            'buy_exchange': ex_b,
                            'sell_exchange': ex_a,
                            'buy_price': best_ask_b,
                            'sell_price': best_bid_a,
                            'profit_percent': profit_percent
                        })
        return opportunities
