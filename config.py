# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Exchange API credentials for Coinbase Pro, Kraken, Bitfinex.
EXCHANGES = {
    "coinbasepro": {
        "apiKey": os.getenv("COINBASEPRO_API_KEY"),
        "secret": os.getenv("COINBASEPRO_API_SECRET"),
        "password": os.getenv("COINBASEPRO_API_PASSWORD"),
    },
    "kraken": {
        "apiKey": os.getenv("KRAKEN_API_KEY"),
        "secret": os.getenv("KRAKEN_API_SECRET"),
    },
    "bitfinex": {
        "apiKey": os.getenv("BITFINEX_API_KEY"),
        "secret": os.getenv("BITFINEX_API_SECRET"),
    },
}

# Trading settings
TRADING_PAIR = "BTC/USD"           # Adjust as needed.
MIN_PROFIT_THRESHOLD = 5.0         # Base profit threshold (5%).
RISK_PER_TRADE = 0.001             # Risk 0.1% of capital per trade.
DAILY_LOSS_LIMIT = 0.01            # 1% daily loss limit.

# Taker fees (example values; adjust as needed)
COINBASEPRO_TAKER_FEE = 0.005      # 0.5%
KRAKEN_TAKER_FEE = 0.0026          # 0.26%
BITFINEX_TAKER_FEE = 0.002          # 0.2%

# Slippage protection
SLIPPAGE_PERCENTAGE = 0.001        # 0.1% slippage

# Dynamic threshold parameters
BASE_MIN_PROFIT_THRESHOLD = 0.05   # 5% base threshold
VOLATILITY_MULTIPLIER = 2.0        # Multiplier for volatility effect
VOLATILITY_WINDOW = 60             # Number of data points (5 minutes if data every 5 sec)

# Cross‑chain settings
ETH_PROVIDER_URL = os.getenv("ETH_PROVIDER_URL")
POLY_PROVIDER_URL = os.getenv("POLY_PROVIDER_URL")
