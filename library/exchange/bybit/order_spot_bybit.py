import sys
import ccxt
from library.exchange.functions import format_symbol, initialize_exchange # Import functions from functions.py


def entry(exchange, args):
    # Build symbol and parameters (Bybit via CCXT expects e.g. 'BTC/USDT')
    symbol = format_symbol(args.pair, format_type='slash')
    type_ = args.order_type  # 'limit' or 'market'
    amount = args.size
    price = args.price if args.order_type == "limit" else None
    
    # Convert direction format
    direction = 'buy' if args.direction in ['buy', 'long'] else 'sell'
    
    # Send the order
    try:
        exchange = initialize_exchange(exchange, args.sandbox, options)
        #exchange.load_markets()
        # CCXT unified create_order
        order = exchange.create_order(
            symbol,
            type_,   # 'market' or 'limit'
            direction,         # 'buy' or 'sell'
            amount,
            price              # None for market orders
        )
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
    """
    Place a stop‑loss (SL) order to exit an existing position via CCXT on Bybit.

    args.pair        # str, e.g. 'BTC/USDT'
    args.direction   # 'buy' or 'sell' for the stop order side
    args.size        # float, amount to close
    args.order_type  # 'market' or 'limit'
    args.price       # float, limit price if using 'limit'
    """
    symbol = format_symbol(args.pair, format_type='slash')
    side = 'sell' if args.direction in ['sell', 'short'] else 'buy'
    amount = args.size
    type_ = args.order_type  # 'market' or 'limit'
    price = args.price if type_ == 'limit' else None

    params = {
        'stopLossPrice': price,
    }

    try:
        current_server_time = exchange.fetch_time()
        order = exchange.create_order(
            symbol,
            type_,
            side,
            amount,
            price,
            params
        )
        print("✅ Stop order placed:")
        print(order)
    except ccxt.BaseError as e:
        print(f"❌ Stop order failed: {str(e)}")
        if hasattr(e, 'response'):
            print("Full error response:")
            print(e.response)
        if hasattr(e, 'http_status'):
            print("HTTP Status Code:", e.http_status)
        sys.exit(1)

def exit(exchange, args):
     print('exit')
