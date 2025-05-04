from bitfinex import WssClient
import json

def handle_orderbook_update(msg):
    # Parse the JSON message
    data = json.loads(msg)
       
    # Extract the order book data
    bids = data[1]['bids']
    asks = data[1]['asks']
       
    # Display the order book in the terminal
    print("\nBids:")
    for bid in bids:
        print(f"Price: {bid[0]}, Amount: {bid[1]}")
           
    print("\nAsks:")
    for ask in asks:
        print(f"Price: {ask[0]}, Amount: {ask[1]}")

# Create a new WebSocket client
wss = WssClient()

# Subscribe to the order book updates for the BTC/USD trading pair
wss.subscribe_to_order_book('tBTCUSD')

# Set the callback function to handle the order book updates
wss.on_order_book_update = handle_orderbook_update

# Connect to the WebSocket API
wss.start()

