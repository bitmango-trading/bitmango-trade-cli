import ccxt
import config

# API credentials
print('CCXT Version:', ccxt.__version__)

# Exchange initialization
exchange = ccxt.binance({
  "enableRateLimit": True,
  "apiKey": config.BINANCE_API_KEY,
  "secret": config.BINANCE_SECRET_KEY,
  #"sandbox": True
})

# Get current market price
symbol = "LINKUSDT"  # Futures contract symbol
ticker = exchange.fetch_ticker(symbol)
current_price = ticker["ask"]  # Use "bid" for a sell order

# Calculate limit price with 10% markup
limit_price = current_price * (1 + 10 / 100)

# Define order parameters
order_type = exchange.ORDER_TYPE_LIMIT  # Set order type to Limit

# Choose either BUY or SELL based on your intention
side = exchange.BUY  # Buying (replace with exchange.SELL for selling)

amount = 1  # Replace with your desired amount (quantity)

# Futures specific parameters (ensure you understand these before using)
leverage = 1  # Set leverage (be cautious with leverage)
positionSide = 'SHORT'  # Set position side to SHORT for selling (use 'LONG' for buying)

# Create the limit order with futures parameters
order = exchange.create_order(symbol, order_type, side, amount, limit_price, {
  'leverage': leverage,
  'positionSide': positionSide
})

# Print the created order details
print(order)
