import time
import ccxt
from pprint import pprint

# spot
exchange = ccxt.binance({enableRateLimit: True})
exchange.load_markets()
pprint(exchange.markets['BTC/USDT'])

sleep(2)

# futures
exchange = ccxt.binance({enableRateLimit: True, 'options': {'defaultType': 'future'}})
exchange.load_markets()
pprint(exchange.markets['BTC/USDT'])