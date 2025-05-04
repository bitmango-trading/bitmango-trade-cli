import argparse
import ccxt
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

# Function to get total free balance
def get_total_balance(currency):
    balances = exchange.fetch_balance()
    return balances['free'][currency]

# Function to place a buy order
def create_buy_order(symbol, price, amount):
    return exchange.create_order(symbol, 'LIMIT', 'BUY', amount, price)

# Function to cancel order
def cancel_order(order_id):
    return exchange.cancel_order(order_id)

# Main logic
def main():
    parser = argparse.ArgumentParser(description='Buy crypto with limit orders')
    parser.add_argument('market_type', choices=['spot', 'futures'], help='Market type (spot or futures)')
    parser.add_argument('symbol', help='Symbol (e.g., BTC/USDT)')
    parser.add_argument('total_position_size', type=float, help='Desired total position size')
    args = parser.parse_args()

    while True:
        try:
            # Get market type and symbol from arguments
            market_type = args.market_type
            symbol = args.symbol
            total_position_size = args.total_position_size

            # Get current price and initial free balance
            price = exchange.fetch_ticker(symbol)['last']
            free_balance = get_total_balance(symbol.split('/')[0])  # Assuming first part is base currency

            # Order amount based on 10% of free balance (capped by total position size)
            order_amount = min(0.1 * free_balance, total_position_size - free_balance)

            while free_balance < total_position_size and order_amount > 0:
                try:
                    # Create limit buy order with target price 0.5% above current price
                    target_price = price * 1.005
                    order = create_buy_order(symbol, target_price, order_amount)

                    # Check if order was successful
                    if order:
                        print(f"Limit buy order created for {order_amount} {symbol} at {target_price}")
                        free_balance += order_amount  # Update free balance (assuming successful fill)

                    # Check if position is filled or timeout after one second
                    if free_balance >= total_position_size or not exchange.fetch_order(order['id'], symbol):
                        if not exchange.fetch_order(order['id'], symbol):
                            # Cancel unfilled order after one second
                            time.sleep(1)
                            if exchange.fetch_order(order['id'], symbol):
                                cancel_order(order['id'])
                                print("Order canceled due to not being filled within one second.")
                        break

                    # Update price for next iteration
                    price = exchange.fetch_ticker(symbol)['last']

                    # Recalculate order amount based on remaining balance
                    order_amount = min(0.1 * (free_balance + order_amount), total_position_size - free_balance)

                except Exception as e:
                    print(f"Error: {e}")
                    break

            if free_balance >= total_position_size:
                print(f"Successfully bought {total_position_size} {symbol}.")
            else:
                print("Unable to buy target position size due to price increase or orders not filled.")

            break  # Exit the loop after one execution

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
