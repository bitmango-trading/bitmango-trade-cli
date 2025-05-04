import sys
import ccxt
from library.exchange.functions import format_symbol # Import functions from functions.py

def entry(exchange, args):
    """
    args.direction   # 'buy' or 'sell'
    args.size        # float
    args.price       # float or None
    args.order_type  # 'market' or 'limit'
    args.pair      # str, e.g. 'btcusdt' or 'BTC/USDT'
    args.no_confirm  # bool
    args.sandbox     # bool
    """

    # Build symbol and parameters
    symbol = format_symbol(args.pair, format_type='underscore')
    type_ = args.order_type  # 'limit' or 'market'
    amount = args.size
    price = args.price if args.order_type == "limit" else None
    
    # Convert direction format
    direction = 'buy' if args.direction in ['buy', 'long'] else 'sell'

    # Send the order
    try:
        if args.order_type == "market":
            order = exchange.create_market_order(symbol, direction, amount)
        else:
            order = exchange.create_limit_order(symbol, direction, amount, price)
        print("✅ Order executed:") # If we reach here, the order was successful
        print(order)
    except ccxt.BaseError as e:
        # Print out the full error message
        print(f"❌ Order failed: {str(e)}")

        # Check if the exception has a 'response' attribute, which contains the full error response
        if hasattr(e, 'response'):
            try:
                # If available, print the response
                print(f"Full error response from {args.exchange}:")
                print(e.response)  # This will give you the raw response from the API
            except Exception as inner_e:
                print("❌ Could not parse error response:", str(inner_e))
        
        # You can also log additional information like the HTTP status code (if available)
        if hasattr(e, 'http_status'):
            print("HTTP Status Code:", e.http_status)

        sys.exit(1)

    if order:  # This checks if the order was created successfully
        print("✅ Order executed:")
        print(order)

def stop(exchange, args):
    print('stop')

def exit(exchange, args):
    print('exit')