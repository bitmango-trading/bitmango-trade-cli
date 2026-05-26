# Account & Management

Commands for monitoring your account, checking market status, and managing existing orders.

## `account`

Displays account-specific data.

**Arguments:**
- `--balance`: Show account balances (total, free, used).
- `--positions`: Show all open positions including entry price and unrealized PnL.

**Examples:**
```bash
./bitmango account --balance --exchange binance
./bitmango account --positions --exchange phemex
```

---

## `markets`

Lists available trading symbols on the selected exchange.

**Example:**
```bash
./bitmango markets --exchange simulated
```

---

## `history`

Displays recent order history for your account.

**Arguments:**
- `--pair`: Optional. Filter history by a specific trading pair.

**Example:**
```bash
./bitmango history --pair BTC-USDT --exchange binance
```

---

## `ledger`

Shows recent account transactions (deposits, withdrawals, funding fees, transfers).

**Arguments:**
- `--currency`: Optional. Default is `USDT`.

**Example:**
```bash
./bitmango ledger --currency BTC --exchange phemex
```

---

## `ticker`

Fetches the latest price, bid/ask spread, and 24h change for a specific pair.

**Example:**
```bash
./bitmango ticker --pair BTC-USDT --exchange phemex
```

---

## `ohlcv`

Fetches historical candlestick data (Open, High, Low, Close, Volume).

**Arguments:**
- `--timeframe`: e.g., `1m`, `5m`, `1h` (default), `1d`.
- `--limit`: Number of candles to return (default: 10).

**Example:**
```bash
./bitmango ohlcv --pair BTC-USDT --timeframe 1h --limit 5 --exchange binance
```

---

## `open_orders`

Shows all currently open orders that have not yet been filled or cancelled.

**Arguments:**
- `--pair`: Optional. Filter open orders by pair.

**Example:**
```bash
./bitmango open_orders --exchange binance
```

---

## `query_order_book`

Displays real-time Level 2 order book data (bids and asks).

**Arguments:**
- `--pair`: **Required.** The trading pair.

**Example:**
```bash
./bitmango query_order_book --pair BTC-USDT --exchange phemex
```

---

## `cancel`

Cancels one or more open orders.

**Arguments:**
- `all`: Cancels ALL open orders for a specific pair.
- `specific`: Cancels a single order matching the criteria (direction and size).

**Examples:**
```bash
# Cancel all orders for BTC-USDT
./bitmango cancel all --pair BTC-USDT --exchange binance

# Cancel a specific 0.1 BTC buy order
./bitmango cancel specific --direction buy --size 0.1 --pair BTC-USDT --exchange phemex
```
