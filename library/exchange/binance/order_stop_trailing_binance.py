import ccxt.async_support as ccxt # link against the asynchronous version of ccxt
import config
import time

# API credentials
print('CCXT Version:', ccxt.__version__)

# Exchange initialization
exchange = ccxt.binance({
    "enableRateLimit": True,
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY,
    #"sandbox": True
})

# Function to check for existing stop-loss order
def has_stop_loss(symbol):
    open_orders = exchange.fetch_open_orders(symbol)
    for order in open_orders:
        if order['type'] == 'STOP_MARKET' and order['side'] == 'SELL':
            return True
    return False

# Function to cancel stop-loss order
def cancel_stop_loss(symbol):
    orders = exchange.fetch_open_orders(symbol)
    for order in orders:
        if order['type'] == 'STOP_MARKET' and order['side'] == 'SELL':
            return exchange.cancel_order(order['id'], symbol)

# Function to create stop-loss order
def create_stop_loss(symbol, price):
    stop_loss_price = price * 0.95  # Adjust the stop-loss ratio (5% in this case)
    return exchange.create_order(
        symbol, 'STOP_MARKET', 'SELL', amount, None, {'stopPrice': stop_loss_price}
    )

# Main logic
while True:
    try:
        # Get user input for market type (spot or futures)
        market_type = input("Enter market type (spot or futures): ")

        # Validate market type
        if market_type.lower() not in ['spot', 'futures']:
            print("Invalid market type. Please enter 'spot' or 'futures'.")
            continue

        # Get user input for symbol
        symbol = input("Enter symbol (e.g., BTC/USDT): ")

        # Futures markets are assumed to be cross margin
        if market_type == 'futures':
            # Check if symbol exists in futures market
            if symbol not in [x['symbol'] for x in exchange.fetch_markets().filter(PERPETUAL=True)]:
                print(f"Symbol {symbol} not found in futures market.")
                continue

            # Loop to continuously monitor price and stop-loss
            while True:
                try:
                    price = exchange.fetch_ticker(symbol)['last']

                    # Check for existing stop-loss
                    if has_stop_loss(symbol):
                        # Cancel existing stop-loss if price has increased
                        if price > exchange.fetch_order(exchange.fetch_open_orders(symbol)[0]['id'], symbol)['price']:
                            cancel_stop_loss(symbol)
                            print("Existing stop-loss canceled.")
                    else:
                        # Create stop-loss at 5% below current price
                        create_stop_loss(symbol, price)
                        print(f"Stop-loss created for {symbol} at {price * 0.95}")

                    time.sleep(10)  # Check price every 10 seconds

                except Exception as e:
                    print(f"Error: {e}")
                    break

        else:
            print("Cross margin stop-loss not supported for spot markets.")

    except Exception as e:
        print(f"Error: {e}")

