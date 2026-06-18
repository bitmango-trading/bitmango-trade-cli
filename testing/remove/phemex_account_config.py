import ccxt
import os
import sys
import time

# Add project root to sys.path to import API_KEYS
sys.path.insert(0, os.getcwd())
from api_keys import API_KEYS

def cleanup_phemex():
    # Initialize with proxy awareness
    API_KEYS.use_sandbox = True
    api_key = API_KEYS.get('phemex', {}).get('api_key')
    secret = API_KEYS.get('phemex', {}).get('secret')
    
    if not api_key or not secret:
        print("Error: Phemex API keys not found")
        return

    exchange = ccxt.phemex({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })
    exchange.set_sandbox_mode(True)
    
    print("--- Phemex Testnet Global Cleanup (Hedge Mode Aware) ---")
    
    try:
        symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT']
        
        for symbol in symbols:
            print(f"\nProcessing {symbol}...")
            try:
                # Cancel open orders
                open_orders = exchange.fetch_open_orders(symbol)
                for order in open_orders:
                    # In Hedged mode, Phemex usually requires posSide for cancellation
                    # Extract it from the raw info if possible
                    pos_side = order['info'].get('posSide', 'Merged')
                    print(f"  Cancelling {order['id']} ({pos_side})...")
                    try:
                        exchange.cancel_order(order['id'], symbol, params={'posSide': pos_side})
                        print("    Success")
                    except Exception as e:
                        print(f"    Failed: {e}")

                # Close positions
                positions = exchange.fetch_positions([symbol])
                for pos in positions:
                    contracts = float(pos.get('contracts', 0))
                    if contracts > 0:
                        side = 'sell' if pos['side'] == 'long' else 'buy'
                        pos_side = 'Long' if pos['side'] == 'long' else 'Short'
                        print(f"  Closing {pos['side']} {contracts} ({pos_side})...")
                        try:
                            exchange.create_order(symbol, 'market', side, contracts, params={'reduceOnly': True, 'posSide': pos_side})
                            print(f"    Closed {symbol}")
                        except Exception as e:
                            print(f"    Failed: {e}")

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        print("\nGlobal Cleanup Complete.")

    except Exception as e:
        print(f"Global Cleanup Error: {e}")

if __name__ == "__main__":
    cleanup_phemex()
