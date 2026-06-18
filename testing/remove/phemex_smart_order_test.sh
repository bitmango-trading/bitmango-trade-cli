#!/bin/bash

# --- Configuration ---
EXCHANGE="phemex"
PAIR="BTC-USDT"
BUY_SIZE="0.003" # Total size to buy
CHUNK_SIZE="0.001" # Size of each chunk
PRICE_RANGE_BUFFER="0.001" # 0.1% buffer for price range

# --- Step 1: Get current BTC price on Phemex testnet ---
echo "Step 1: Getting current BTC price on Phemex testnet..."
ORDER_BOOK_OUTPUT=$(./bitmango --sandbox query_order_book --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures)
BEST_ASK=$(echo "$ORDER_BOOK_OUTPUT" | awk '/Asks:/ {getline; print $2}' | sed 's/,//')

if [ -z "$BEST_ASK" ]; then
    echo "Error: Could not get best ask price. Exiting."
    exit 1
fi

echo "Current Best Ask for $PAIR: $BEST_ASK"

# --- Step 2: Calculate entry price and price range ---
ENTRY_PRICE=$(printf "%.1f" "$BEST_ASK")

# Calculate price range for smart order
PRICE_RANGE_MIN=$(python -c "print($ENTRY_PRICE * (1 - $PRICE_RANGE_BUFFER))")
PRICE_RANGE_MAX=$(python -c "print($ENTRY_PRICE * (1 + $PRICE_RANGE_BUFFER))")

echo "Calculated Entry Price: $ENTRY_PRICE"
echo "Calculated Price Range: $PRICE_RANGE_MIN - $PRICE_RANGE_MAX"

# --- Step 3: Execute the smart entry order (limit buy) ---
echo "Step 3: Executing smart entry order..."
./bitmango --sandbox entry --exchange "$EXCHANGE" --pair "$PAIR" --market-type futures \
    --order-type limit --direction buy --size "$BUY_SIZE" --price "$ENTRY_PRICE" \
    --smart-order --chunk-size "$CHUNK_SIZE" \
    --price-range-min "$PRICE_RANGE_MIN" --price-range-max "$PRICE_RANGE_MAX" \
    --no-confirm <<< "y"

echo "Test script finished. Please manually verify orders on Phemex testnet."
