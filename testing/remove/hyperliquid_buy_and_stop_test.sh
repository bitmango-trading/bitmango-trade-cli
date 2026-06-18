#!/bin/bash

# --- Configuration ---
EXCHANGE="hyperliquid"
PAIR="BTC-USD"
BUY_SIZE="0.1"
STOP_PERCENT="0.01" # 1%

# --- Step 1: Get current BTC price on Hyperliquid testnet ---
echo "Step 1: Getting current BTC price on Hyperliquid testnet..."
# This command is currently failing due to bitmango corruption.
# Once bitmango is fixed, this command should output order book data.
# We will need to parse the best ask price from its output.
# For now, we'll use a placeholder price.
#
# Example of expected output (simplified):
# --- Order Book for BTC ---
# Bids:
#   Price: 60000.0, Size: 1.5
# Asks:
#   Price: 60001.0, Size: 2.0
#
# Replace this with actual bitmango command once fixed:
# ORDER_BOOK_OUTPUT=$(./bitmango query_order_book --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures --sandbox)
# BEST_ASK=$(echo "$ORDER_BOOK_OUTPUT" | grep "Price:" | head -n 2 | tail -n 1 | awk '{print $2}' | sed 's/,//')

# Placeholder for best ask price (replace with actual parsed value)
BEST_ASK="60000.0" # Example placeholder price

if [ -z "$BEST_ASK" ]; then
    echo "Error: Could not get best ask price. Exiting."
    exit 1
fi

echo "Current Best Ask for $PAIR: $BEST_ASK"

# --- Step 2: Calculate entry price and stop price ---
# For a buy limit order, we'll try to buy at the best ask or slightly below.
# For this test, let's assume we target the best ask as our entry price.
ENTRY_PRICE=$(echo "$BEST_ASK" | awk '{printf "%.1f", $1}') # Round to 1 decimal for example

# Calculate stop price (1% below entry price)
STOP_PRICE=$(echo "$ENTRY_PRICE * (1 - $STOP_PERCENT)" | bc -l | awk '{printf "%.1f", $1}') # Round to 1 decimal for example

echo "Calculated Entry Price: $ENTRY_PRICE"
echo "Calculated Stop Price (1% below): $STOP_PRICE"

# --- Step 3: Execute the entry order (limit buy) ---
echo "Step 3: Executing entry order..."
# Replace with actual bitmango command once fixed:
# ./bitmango entry --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures --order-type limit --direction buy --size "$BUY_SIZE" --price "$ENTRY_PRICE" --sandbox --no-confirm
echo "Placeholder: Executed entry order for $BUY_SIZE $PAIR at $ENTRY_PRICE"

# --- Step 4: Execute the market stop order ---
echo "Step 4: Executing market stop order..."
# Replace with actual bitmango command once fixed:
# ./bitmango stop --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures --order-type market --direction sell --size "$BUY_SIZE" --price "$STOP_PRICE" --sandbox --no-confirm
echo "Placeholder: Executed market stop order for $BUY_SIZE $PAIR at $STOP_PRICE"

echo "Test script finished. Please manually verify orders on Hyperliquid testnet."