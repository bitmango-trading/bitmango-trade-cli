#!/bin/bash

# --- Configuration ---
EXCHANGE="phemex"
PAIR="BTC-USDT" # Changed to USDT for Phemex
BUY_SIZE="0.001" # Adjusted to match Phemex's returned size
STOP_PERCENT="0.01" # 1%

# --- Step 1: Get current BTC price on Phemex testnet ---
echo "Step 1: Getting current BTC price on Phemex testnet..."
# This command should output order book data.
# We will need to parse the best ask price from its output.
ORDER_BOOK_OUTPUT=$(./bitmango --sandbox query_order_book --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures)
BEST_ASK=$(echo "$ORDER_BOOK_OUTPUT" | awk '/Asks:/ {getline; print $2}' | sed 's/,//')

if [ -z "$BEST_ASK" ]; then
    echo "Error: Could not get best ask price. Exiting."
    exit 1
fi # Added missing fi

echo "Current Best Ask for $PAIR: $BEST_ASK"

# --- Step 2: Calculate entry price and stop price ---
# For a buy limit order, we'll try to buy at the best ask or slightly below.
# For this test, let's assume we target the best ask as our entry price.
ENTRY_PRICE=$(printf "%.1f" "$BEST_ASK") # Round to 1 decimal for example

# Calculate stop price (1% below entry price)
# Ensure ENTRY_PRICE is treated as a float for bc
STOP_PRICE_CALC=$(python -c "print($ENTRY_PRICE * (1 - $STOP_PERCENT))")
STOP_PRICE=$(printf "%.1f" "$STOP_PRICE_CALC") # Round to 1 decimal for example

echo "Calculated Entry Price: $ENTRY_PRICE"
echo "Calculated Stop Price (1% below): $STOP_PRICE"

# --- Step 3: Execute the entry order (limit buy) ---
echo "Step 3: Executing entry order..."
# Round BUY_SIZE to the nearest 0.001 increment
ROUNDED_BUY_SIZE=$(awk -v num="$BUY_SIZE" -v step="0.001" 'BEGIN {print int(num/step + 0.5) * step}')

./bitmango --sandbox entry --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures --order-type limit --direction buy --size "$ROUNDED_BUY_SIZE" --price "$ENTRY_PRICE" <<< "y"
echo "Placeholder: Executed entry order for $ROUNDED_BUY_SIZE $PAIR at $ENTRY_PRICE"

# --- Step 4: Execute the market stop order ---
echo "Step 4: Executing market stop order..."
./bitmango --sandbox stop --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures --order-type market --direction sell --size "$ROUNDED_BUY_SIZE" --price "$STOP_PRICE" <<< "y"
echo "Placeholder: Executed market stop order for $ROUNDED_BUY_SIZE $PAIR at $STOP_PRICE"

echo "Test script finished. Please manually verify orders on Phemex testnet."