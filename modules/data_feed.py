# modules/data_feed.py
import asyncio
import numpy as np
import ccxt.async_support as ccxt
from ccxt.base.errors import NetworkError, RateLimitExceeded, ExchangeError, InsufficientFunds, InvalidOrder, AuthenticationError
from config import EXCHANGES, TRADING_PAIR, VOLATILITY_WINDOW
from modules.logger import setup_logger

logger = setup_logger("DataFeed", log_file="logs/data_feed.log")

# Explicit mapping for async exchanges:
EXCHANGE_MAPPING = {
    "coinbase": ccxt.coinbase,
    "kraken": ccxt.kraken,
    "bitfinex": ccxt.bitfinex,
}

async def fetch_order_book_with_retry(exchange, symbol, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return await asyncio.wait_for(exchange.fetch_order_book(symbol), timeout=5)
        except (NetworkError, RateLimitExceeded) as e:
            logger.error(f"Network/RateLimit error from {exchange.name} (attempt {attempt+1}): {e}. Retrying...")
            await asyncio.sleep(delay)
        except ExchangeError as e:
            logger.error(f"Exchange error from {exchange.name} (attempt {attempt+1}): {e}.")
            return None
        except (InsufficientFunds, InvalidOrder) as e:
            logger.error(f"{type(e).__name__} from {exchange.name}: {e}. Check account/order.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error from {exchange.name} (attempt {attempt+1}): {e}")
            await asyncio.sleep(delay)
    return None

class DataFeed:
    def __init__(self):
        self.exchanges = {}
        self.mid_prices = {}  # For volatility

    @classmethod
    async def create(cls):
        self = cls()
        for name, creds in EXCHANGES.items():
            try:
                exchange_class = EXCHANGE_MAPPING.get(name)
                if not exchange_class:
                    raise ValueError(f"No mapping for exchange: {name}")
                instance = exchange_class({
                    'apiKey': creds.get("apiKey"),
                    'secret': creds.get("secret"),
                    'password': creds.get("password", None),
                    'enableRateLimit': True,
                })
                try:
                    await asyncio.wait_for(instance.fetch_balance(), timeout=10)
                    logger.info(f"Successfully connected to {name}")
                except AuthenticationError as e:
                    logger.error(f"Authentication error with {name}: {e}. Check API keys.")
                    continue
                except Exception as e:
                    logger.error(f"Error validating exchange {name}: {e}")
                    continue
                self.exchanges[name] = instance
            except Exception as e:
                logger.error(f"Error initializing {name}: {e}")
        return self

    async def fetch_order_book(self, exchange, symbol=TRADING_PAIR):
        order_book = await fetch_order_book_with_retry(exchange, symbol)
        if order_book:
            self.update_mid_prices(exchange.name, order_book)
        return order_book

    def update_mid_prices(self, exchange_name, order_book):
        best_bid = order_book['bids'][0][0] if order_book.get('bids') else None
        best_ask = order_book['asks'][0][0] if order_book.get('asks') else None
        if best_bid is None or best_ask is None:
            return
        mid_price = (best_bid + best_ask) / 2
        if exchange_name not in self.mid_prices:
            self.mid_prices[exchange_name] = []
        self.mid_prices[exchange_name].append(mid_price)
        if len(self.mid_prices[exchange_name]) > VOLATILITY_WINDOW:
            self.mid_prices[exchange_name].pop(0)

    def get_volatility(self, exchange_name):
        if exchange_name not in self.mid_prices or len(self.mid_prices[exchange_name]) < VOLATILITY_WINDOW:
            return 0
        return np.std(self.mid_prices[exchange_name])

    async def get_all_order_books(self):
        tasks = [self.fetch_order_book(exchange, TRADING_PAIR) for exchange in self.exchanges.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        order_books = dict(zip(self.exchanges.keys(), results))
        return order_books

    async def close_exchanges(self):
        tasks = [exchange.close() for exchange in self.exchanges.values()]
        await asyncio.gather(*tasks)
