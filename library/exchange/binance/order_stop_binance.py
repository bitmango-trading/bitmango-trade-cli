# For binance, you can read the actual program code at
# https://github.com/ccxt/ccxt/blob/master/python/ccxt/binance.py#L2624

# I use it for 'SANDBUSD' pair, based on market price.
# Coins is the total coins, in this case, the total SAND coins

# Futures code for LONG:
# params = { 'stopPrice': stop_price_here } #lower than actual price
# order =  exchange.createOrder('SANDBUSD', 'MARKET', 'buy', coins, None, params)

# Futures code for SHORT:
# params = { 'stopPrice': stop_price_here  } #higher than actual price
# order =  exchange.createOrder('SANDBUSD', 'MARKET', 'sell', coins, None, params)

import argparse
import ccxt.async_support as ccxt # link against the asynchronous version of ccxt
import config
import time

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Manage stop-loss orders on Binance')
parser.add_argument('--market', choices=['spot', 'futures'], required=True, help='Market type (spot or futures)')
parser.add_argument('--pair', type=str, required=True, help='Symbol (e.g., SANDBUSD)')
parser.add_argument('--position', choices=['long', 'short'], required=True, help='Position type (long or short)')
parser.add_argument('--stop_price', type=float, required=True, help='Stop-loss price')
parser.add_argument('--coins', type=float, required=True, help='Total coins (e.g., total SAND coins)')
args = parser.parse_args()

# API credentials
print('CCXT Version:', ccxt.__version__)

# Exchange initialization
exchange = ccxt.binance({
    "enableRateLimit": True,
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY,
    #"sandbox": True
})


# Function to create stop-loss order (modified)
def create_stop_loss(symbol, position, stop_price, coins):
  side = 'buy' if position == 'long' else 'sell'
  params = {'stopPrice': stop_price}
  order = exchange.create_order(symbol, 'MARKET', side, coins, None, params)
  print(f"Stop-loss {position} order created for {symbol} at {stop_price}")

# Main logic
market_type = args.market
symbol = args.pair
position = args.position
stop_price = args.stop_price
coins = args.coins

if market_type != 'futures':
  print("Stop-loss orders are only supported for futures markets.")
  exit()

create_stop_loss(symbol, position, stop_price, coins)

# Pause for a while before checking again
time.sleep(60)  # Adjust the interval as needed

await exchange.close()