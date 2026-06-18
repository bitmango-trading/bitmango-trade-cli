# Bot Integration: Building an Institutional Execution Engine

BitMango Trade CLI isn't just for humans—it's designed to be the high-performance execution core for your custom trading infrastructure. By offloading complex exchange logic to BitMango, you can focus 100% on your alpha-generating strategy.

---

## The Bot Developer's Dilemma
Every exchange has a different API, different error codes, different precision rules, and different rate limits. Building a multi-exchange bot usually requires thousands of lines of "glue code" just to keep it from crashing.

## The BitMango Advantage
BitMango standardizes the entire experience. Your bot sends a command to BitMango, and BitMango handles the heavy lifting:
- **Exchange Agnostic:** Use the same JSON parser for Binance, Phemex, and Bybit.
- **Hardened Error Handling:** BitMango catches exchange-side quirks and returns standardized JSON error objects.
- **Precision Management:** BitMango automatically formats sizes and prices to meet each exchange's specific requirements.

---

## ⚡ JSON Mode (`-o json`)

For programmatic use, always enable the global `--output json` flag.

### 🛡️ Why use it?
1.  **Pure Stdout:** BitMango uses a `SilentStderrWrapper` to ensure `stdout` contains **exactly one** valid JSON object. 
2.  **Integrated Logs:** All warnings, debug info, and informational messages that would normally go to `stderr` are instead captured and nested under a top-level `"logs"` key in the JSON response.
3.  **Predictable Exit Codes:** JSON mode translates technical failures (e.g. `RISK BREACH`) into specific `status` fields and non-zero exit codes.

---

## 🧩 JSON Schema Reference

### Top-Level Keys
Every JSON response contains:
- `status`: "success", "error", "risk_breach", or "permission_denied".
- `logs`: (Optional) An array of log objects `{"level": "...", "message": "..."}`.
- `exit_code`: Mirror of the process exit code.

### 1. Market Data

#### `ticker --pair BTC-USDT`
```json
{
  "type": "ticker",
  "exchange": "simulated",
  "symbol": "BTC/USDT",
  "data": {
    "symbol": "BTC/USDT",
    "last": 50000.0,
    "bid": 49995.0,
    "ask": 50005.0,
    "percentage": 2.5
  },
  "status": "success",
  "logs": [...]
}
```

#### `ohlcv --pair BTC-USDT --limit 1`
```json
{
  "type": "ohlcv",
  "exchange": "simulated",
  "data": [
    {
      "timestamp": 1772602095000,
      "open": 49000.0,
      "high": 50000.0,
      "low": 48000.0,
      "close": 49500.0,
      "volume": 10.5,
      "indicators": {
        "rsi": 65.2,
        "ema": 49200.1
      }
    }
  ],
  "status": "success"
}
```

#### `account --positions`
```json
{
  "type": "positions",
  "exchange": "simulated",
  "positions": [
    {
      "symbol": "BTCUSDT",
      "side": "long",
      "size": 0.1,
      "entry_price": 70000.0,
      "unrealized_pnl": 45.20,
      "leverage": 10.0,
      "margin_mode": "isolated"
    }
  ]
}
```

#### `history`
```json
{
  "type": "history",
  "exchange": "simulated",
  "orders": [
    {
      "id": "100234",
      "datetime": "2026-02-19T10:00:00Z",
      "symbol": "BTC/USDT",
      "side": "buy",
      "type": "market",
      "amount": 0.1,
      "price": 69500.0,
      "status": "closed",
      "filled": 0.1,
      "remaining": 0.0
    }
  ]
}
```

#### `ledger`
```json
{
  "type": "ledger",
  "exchange": "simulated",
  "currency": "USDT",
  "entries": [
    {
      "id": "72134",
      "datetime": "2026-02-18T17:35:57Z",
      "type": "TRANSFER",
      "amount": 100.0,
      "currency": "USDT",
      "status": "COMPLETED"
    }
  ]
}
```

---

### 2. Order Execution

#### `buy` / `sell` / `entry`
```json
{
  "type": "order",
  "exchange": "simulated",
  "order": {
    "id": "4",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "market",
    "amount": 0.1,
    "price": 0.0,
    "status": "filled",
    "filled": 0.1,
    "remaining": 0.0
  }
}
```

#### `open_orders`
```json
{
  "type": "open_orders",
  "exchange": "simulated",
  "orders": [
    {
      "id": "6",
      "symbol": "BTCUSDT",
      "side": "sell",
      "type": "limit",
      "amount": 0.1,
      "price": 70000.0,
      "status": "new"
    }
  ]
}
```

#### `cancel all`
```json
{
  "type": "cancel_all",
  "exchange": "simulated",
  "symbol": "BTCUSDT",
  "status": "success"
}
```

---

### 3. Stop Orders (Core & Pro)

#### Native Stops (Core)
```json
{
  "type": "order",
  "exchange": "simulated",
  "order": {
    "id": "7",
    "symbol": "BTCUSDT",
    "side": "buy",
    "type": "stop_market",
    "amount": 0.1,
    "price": 65000.0,
    "status": "new",
    "filled": 0.0,
    "remaining": 0.1
  }
}
```

#### Trailing / Ghost Stops (PRO Binary)
```json
{
  "type": "order",
  "status": "monitoring",
  "message": "Stealth stop monitoring started"
}
```

---

### 4. Risk & Configuration

#### `leverage`
```json
{
  "type": "set_leverage",
  "exchange": "simulated",
  "symbol": "BTC-USDT",
  "leverage": 10,
  "status": "success"
}
```

#### `margin`
```json
{
  "type": "set_margin_mode",
  "exchange": "simulated",
  "symbol": "BTC-USDT",
  "mode": "isolated",
  "status": "success"
}
```

#### `transfer`
```json
{
  "type": "transfer",
  "exchange": "simulated",
  "currency": "USDT",
  "amount": 100.0,
  "from": "spot",
  "to": "futures",
  "status": "success"
}
```

---

### 5. Market Data

#### `markets`
```json
{
  "type": "markets",
  "exchange": "simulated",
  "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
}
```

#### `funding`
```json
{
  "type": "funding_rate",
  "exchange": "simulated",
  "symbol": "BTCUSDT",
  "rate": 0.0001,
  "status": "success"
}
```

#### `query_order_book`
```json
{
  "type": "order_book",
  "exchange": "simulated",
  "symbol": "BTCUSDT",
  "bids": [[70000.0, 1.0], [69990.0, 2.5]],
  "asks": [[70010.0, 0.5], [70020.0, 1.2]]
}
```

---

## 🛠️ Error Handling

When an operation fails, BitMango returns a standardized error object.

```json
{
  "type": "order",
  "status": "error",
  "message": "Insufficient balance to place order"
}
```

---

## 🚀 Practical Bot Examples

### 1. Unified Portfolio Dashboard (Shell + `jq`)
Combine balance and positions into a single report:
```bash
#!/bin/bash
EXCHANGE="binance"
echo "--- Account Health ---"
./bitmango account --balance -e $EXCHANGE -o json | jq '.balances[] | select(.total > 0)'
./bitmango account --positions -e $EXCHANGE -o json | jq '.positions[]'
```

### 2. High-Speed Scalping Loop (Python)
Execute trades based on order book depth:
```python
import subprocess
import json
import time

def get_spread(pair):
    res = subprocess.run(["./bitmango", "query_order_book", "--pair", pair, "-e", "binance", "-o", "json"], capture_output=True, text=True)
    book = json.loads(res.stdout)
    return book['asks'][0][0] - book['bids'][0][0]

while True:
    spread = get_spread("BTC-USDT")
    if spread > 50:
        print(f"Scalp opportunity! Spread: {spread}")
        # Place limit orders...
    time.sleep(1)
```

---

## 🛠️ Bot Developer Pro-Tips

### 1. The `stderr` Log Stream
Always capture `stderr` in your bot logs. BitMango prints real-time health warnings and connection attempts there, which are invaluable for debugging production issues without breaking your JSON parser.

### 2. Standardized Status Codes
BitMango maps complex exchange-specific statuses into a unified set:
- `open`: Order is in the book.
- `closed`: Order is fully filled.
- `canceled`: Order was removed before filling.

### 3. Rate Limit Resilience
BitMango includes built-in retry logic for 429 (Rate Limit) and 5xx (Exchange Error) responses. Your bot doesn't need to implement its own backoff logic—BitMango does it for you.
