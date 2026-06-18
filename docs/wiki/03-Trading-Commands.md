# Trading Commands

The BitMango Trade CLI provides a standardized set of commands for placing and managing orders across different exchanges.

## `entry` (Buy/Sell)

The primary command for opening a new position or increasing an existing one.

**Arguments:**
- `--direction`: `buy` (or `long`), `sell` (or `short`). **Required.**
- `--size`: The size of the trade (e.g., `0.1`).
- `--percent`: Alternative to size; uses a percentage of available balance.
- `--order-type`: `market` (default) or `limit`.
- `--price`: The limit price (required for `limit` orders).
- `--pair`: The trading pair (e.g., `BTC-USDT`).
- `--smart-order`: Enables TWAP-based smart execution. See [Advanced Strategies](05-Advanced-Strategies.md).

**Examples:**
```bash
./bitmango entry --direction buy --size 0.5 --pair BTC-USDT --exchange binance
./bitmango entry --direction sell --order-type limit --price 72000 --size 0.1 --pair BTC-USDT --exchange phemex
```

### Aliases: `buy` and `sell`
For convenience, you can use `buy` and `sell` directly:
```bash
./bitmango buy --size 0.1 --pair BTC-USDT --exchange simulated
./bitmango sell --percent 50 --pair ETH-USDT --exchange binance
```

---

## `exit` / `close`

Commands used to reduce or close a position.

**Arguments:**
- `--size`: The amount to exit.
- `--order-type`: `market` (default) or `limit`.
- `--pair`: The trading pair.
- `--exit_command`: `all` (closes entire position) or `specific` (default).

### Aliases: `close` and `close-all`
- `close --pair <PAIR>`: Closes the specific position.
- `close-all`: Closes ALL open positions on the exchange.

**Examples:**
```bash
./bitmango exit specific --size 0.5 --pair BTC-USDT --exchange phemex
./bitmango close --pair BTC-USDT --exchange binance
./bitmango close-all --exchange binance
```

---

## `stop` (CORE)

Sets a stop-loss or take-profit order. By default, this uses **Native Stops** (exchange-side execution). 

**Core Support Includes:**
- **Market Stop:** Closes position at market price when triggered.
- **Limit Stop:** Places a limit order when triggered.
- **Native Trailing Stop:** Uses the exchange's built-in trailing logic (if supported by the exchange).

**Arguments:**
- `--direction`: The direction of the *original* entry (the stop will be in the opposite direction).
- `--size`: The size of the stop order.
- `--stop-price`: The trigger price.
- `--stop-type`: `native` (default).
- `--order-type`: `market`, `limit`, `stop_loss`, `take_profit`.

**Examples:**
```bash
# Native market stop
./bitmango stop --stop-price 65000 --size 0.1 --pair BTC-USDT --exchange binance
```
*Note: For Ghost Stops and CLI-side Trailing Stops, see [Advanced Strategies (PRO)](05-Advanced-Strategies.md).*

---

## Market Data (CORE)

Standardized commands for pulling real-time and historical market data. These commands do **not** require API keys.

### `markets`
Lists all tradable pairs supported by the exchange.
```bash
./bitmango markets --exchange binance
```

### `ticker`
Fetches the latest price, bid/ask spread, and 24h change for a specific pair.
```bash
./bitmango ticker --pair BTC-USDT --exchange phemex
```

### `ohlcv`
Fetches historical candlestick data (Open, High, Low, Close, Volume).
**Arguments:**
- `--timeframe`: e.g., `1m`, `5m`, `1h` (default), `1d`.
- `--limit`: Number of candles to return (default: 10).

```bash
./bitmango ohlcv --pair BTC-USDT --timeframe 1h --limit 5 --exchange binance
```

### `query_order_book`
Queries the L2 order book (depth).
```bash
./bitmango query_order_book --pair BTC-USDT --exchange bybit
```

### `funding`
Fetches the current funding rate for futures pairs.
```bash
bitmango funding --pair BTC-USDT --exchange bitget
```

---

## Order Tracking & History

### `open_orders`
Lists all active orders currently in the order book.
```bash
bitmango open_orders --pair BTC-USDT --exchange binance
```

### `order-status`
Fetch the full details and current status of a specific order by its UUID.
```bash
bitmango order-status --order-id "123456" --pair BTC-USDT --exchange bybit
```

### `closed-orders`
Lists recently filled or cancelled orders.
```bash
bitmango closed-orders --pair BTC-USDT --limit 20 --exchange phemex
```

### `trades`
Lists your actual executions (fills) for a specific pair.
```bash
bitmango trades --pair BTC-USDT --exchange binance
```

### `ledger`
Fetch your account's financial transaction history (deposits, withdrawals, fees, transfers).
```bash
bitmango ledger --currency USDT --exchange simulated
```
