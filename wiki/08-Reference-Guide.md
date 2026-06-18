# CLI Reference Guide

This guide contains the legacy reference for core commands. Most of this information is now organized into specific sections in the Wiki.

## Core Commands

### `entry`
Place an entry order.
- `--market-type`: `spot` or `futures` (default: `spot`)
- `--order-type`: `market` or `limit`
- `--direction`: `buy` or `sell`
- `--size`: The size of the trade
- `--price`: The limit price (for limit orders)
- `--pair`: The trading pair (e.g., `BTC-USD`)
- `--smart-order`: Use smart order strategy.

### `exit`
Place an exit order to close a position.
- `--market-type`: `spot` or `futures` (default: `spot`)
- `--order-type`: `market` or `limit`
- `--direction`: `buy` or `sell`
- `--size`: The size of the trade to close.

### `stop`
Place a stop order.
- `--market-type`: `spot` or `futures` (default: `spot`)
- `--order-type`: `market` or `limit`
- `--price`: The trigger price
- `--size`: The size of the trade
- `--smart-stop`: Use smart stop strategy.

### `cancel`
Cancel an open order.
- `all`: Cancel all open orders.
- `specific`: Cancel by pair, direction, and size.

### `account`
View account information.
- `--balance`: Show account balance.
- `--positions`: Show open positions.

### `query_order_book`
Get real-time order book data.
