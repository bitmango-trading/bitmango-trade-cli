import sys
import ccxt
from library.exchange.functions import format_symbol

def entry(exchange, args):
    """
    Phemex-specific execution with changes for:
    - Symbol formatting (requires colon format: BTC/USDT:USD)
    - Order type handling
    - Phemex-specific error responses
    - Sandbox mode handling
    """
    # Initialize Phemex exchange
    exchange = ccxt.phemex({
        'enableRateLimit': True,
        'apiKey': exchange.apiKey,
        'secret': exchange.secret,
    })

    if args.sandbox:
        exchange.set_sandbox_mode(True)

    # Phemex requires symbols in format BTC/USDT:USD for linear contracts
    symbol = format_symbol(args.pair, format_type='slash-colon')  
    
    # Convert direction format
    direction = 'buy' if args.direction in ['buy', 'long'] else 'sell'
    
    # Phemex order parameters
    params = {
        'timeInForce': 'PostOnly' if args.order_type == 'limit' else 'ImmediateOrCancel',
        'type': 'Market' if args.order_type == 'market' else 'Limit',
    }

    try:
        # Unified order creation for Phemex
        order = exchange.create_order(
            symbol=symbol,
            type=params['type'],
            side=direction,
            amount=args.size,
            price=args.price if args.order_type == 'limit' else None,
            params=params
        )

        if order['status'] == 'closed' or order['status'] == 'filled':
            print("✅ Order executed successfully:")
            print(f"ID: {order['id']}")
            print(f"Filled: {order['filled']}")
            print(f"Average Price: {order['average']}")
        else:
            print("⚠️ Order placed but not immediately filled:")
            print(f"ID: {order['id']}")
            print(f"Status: {order['status']}")

    except ccxt.BaseError as e:
        print(f"❌ Phemex API Error: {str(e)}")
        
        # Handle common Phemex-specific errors
        if 'insufficient balance' in str(e).lower():
            print("💸 Error: Insufficient balance for this order")
        elif 'invalid symbol' in str(e).lower():
            print(f"🔣 Invalid symbol format - Phemex requires format like BTC/USDT:USD")
        
        # Debugging information
        if hasattr(e, 'response'):
            print(f"📄 Phemex error response:")
            print(e.response.text)  # Raw response often contains important details
            
        sys.exit(1)

    # Additional Phemex order checks
    if order.get('info', {}).get('ordRejReason'):
        print(f"⚠️ Order rejected reason: {order['info']['ordRejReason']}")

    return order