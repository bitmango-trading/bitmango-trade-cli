#!/bin/bash

# --- Configuration ---
EXCHANGE="bybit"
PAIR="BTC-USDT" # Changed to USDT for Bybit
ENTRY_BUY_SIZE="0.001" # Size for the initial entry order
TAKE_PROFIT_PERCENT="0.02" # 2%

# --- Step 1: Get current BTC price on Bybit testnet ---
echo "Step 1: Getting current BTC price on Bybit testnet..."
ORDER_BOOK_OUTPUT=$(./bitmango --sandbox query_order_book --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures)
BEST_ASK=$(echo "$ORDER_BOOK_OUTPUT" | awk '/Asks:/ {getline; print $2}' | sed 's/,//')

if [ -z "$BEST_ASK" ]; then
    echo "Error: Could not get best ask price. Exiting."
    exit 1
fi

echo "Current Best Ask for $PAIR: $BEST_ASK"

# --- Step 2: Place an initial entry order to create an open position ---
echo "Step 2: Placing an initial entry order..."
ENTRY_PRICE=$(printf "%.1f" "$BEST_ASK")
./bitmango --sandbox entry --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures \
    --order-type limit --direction buy --size "$ENTRY_BUY_SIZE" --price "$ENTRY_PRICE" \
    --no-confirm <<< "y"

echo "Initial entry order placed. Waiting for it to fill (manual verification needed)."
sleep 10 # Give some time for the order to potentially fill on the testnet

# --- Step 3: Execute the smart stop command ---
echo "Step 3: Executing the smart stop command..."
# The smart stop will continuously monitor the position and price.
# It will run indefinitely until the position is closed or the script is manually stopped.
./bitmango --sandbox stop --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures \
    --direction buy --size "$ENTRY_BUY_SIZE" --smart-stop --no-confirm <<< "y"

echo "Test script finished. Monitor the output for smart stop behavior."
