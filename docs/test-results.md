# Trade CLI Test Results (bitmango-bitmango)

Date: Sat  6 Sep 00:57:31 BST 2025

## Test Summary

### Phemex - Fetch Account Balance (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.phemex.account_open_positions
Loaded module: bitmango.exchange.phemex.account_open_positions
Using Phemex Mainnet
Error: Could not find class PhemexAccountPositions or required method in module bitmango.exchange.phemex.account_open_positions
Please ensure the class and method names are correct in the exchange-specific module.

Stderr: 
Return Code: 1
```

### Phemex - Fetch Account Balance (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Phemex - Fetch Open Positions (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.phemex.account_open_positions
Loaded module: bitmango.exchange.phemex.account_open_positions
Using Phemex Mainnet
Error: Could not find class PhemexAccountPositions or required method in module bitmango.exchange.phemex.account_open_positions
Please ensure the class and method names are correct in the exchange-specific module.

Stderr: 
Return Code: 1
```

### Phemex - Fetch Open Positions (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Phemex - Query Order Book (Mainnet) - BTC/USDT
- Status: PASS
- Details:
```
Debug: Attempting to import module: bitmango.exchange.phemex.query_orderbook_phemex
Debug: Successfully imported module: bitmango.exchange.phemex.query_orderbook_phemex
Debug: Attempting to get class: PhemexQueryOrderBook from module: bitmango.exchange.phemex.query_orderbook_phemex
Debug: Successfully got class: PhemexQueryOrderBook
Using Phemex Mainnet
Market info for BTC/USDT:USDT:
  Price Precision: 0.1
  Minimum Price: None
  Amount Step Size: 0.0001
--- Order Book for BTC/USDT:USDT ---
Bids:
  Price: 110590.0, Size: 0.0002
  Price: 110589.9, Size: 0.0002
  Price: 110589.8, Size: 0.1337
  Price: 110589.7, Size: 0.0002
  Price: 110589.6, Size: 0.0002
Asks:
  Price: 110590.1, Size: 8.0902
  Price: 110590.2, Size: 0.4135
  Price: 110590.5, Size: 0.036
  Price: 110590.6, Size: 0.022
  Price: 110591.4, Size: 1.6845
----------------------------------

```

### Phemex - Query Order Book (Testnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Bybit - Fetch Account Balance (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.bybit.account_bybit
Loaded module: bitmango.exchange.bybit.account_bybit
Using Bybit Mainnet
Error fetching balance: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757116656073}

Stderr: 
Return Code: 1
```

### Bybit - Fetch Account Balance (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Bybit - Fetch Open Positions (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.bybit.account_bybit
Loaded module: bitmango.exchange.bybit.account_bybit
Using Bybit Mainnet
Error fetching positions: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757116656889}

Stderr: 
Return Code: 1
```

### Bybit - Fetch Open Positions (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Bybit - Query Order Book (Mainnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: Debug: Attempting to import module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Successfully imported module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Attempting to get class: BybitQueryOrderBook from module: bitmango.exchange.bybit.query_orderbook_bybit
Debug: Successfully got class: BybitQueryOrderBook
Using Bybit Mainnet
Error querying order book: bybit {"retCode":10003,"retMsg":"API key is invalid.","result":{},"retExtInfo":{},"time":1757116657703}

Stderr: 
Return Code: 1
```

### Bybit - Query Order Book (Testnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Mexc - Fetch Account Balance (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.mexc.account_mexc
Loaded module: bitmango.exchange.mexc.account_mexc
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Mexc - Fetch Account Balance (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Mexc - Fetch Open Positions (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.mexc.account_mexc
Loaded module: bitmango.exchange.mexc.account_mexc
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Mexc - Fetch Open Positions (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Mexc - Query Order Book (Mainnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: Debug: Attempting to import module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Successfully imported module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Attempting to get class: MexcQueryOrderBook from module: bitmango.exchange.mexc.query_orderbook_mexc
Debug: Successfully got class: MexcQueryOrderBook
Error: API keys for mexc are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Mexc - Query Order Book (Testnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Hyperliquid - Fetch Account Balance (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.hyperliquid.account_hyperliquid
Error: Could not find module at bitmango.exchange.hyperliquid.account_hyperliquid
Please ensure the file exists and the naming convention is correct.

Stderr: 
Return Code: 1
```

### Hyperliquid - Fetch Account Balance (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Hyperliquid - Fetch Open Positions (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.hyperliquid.account_hyperliquid
Error: Could not find module at bitmango.exchange.hyperliquid.account_hyperliquid
Please ensure the file exists and the naming convention is correct.

Stderr: 
Return Code: 1
```

### Hyperliquid - Fetch Open Positions (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Hyperliquid - Query Order Book (Mainnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: Debug: Attempting to import module: bitmango.exchange.hyperliquid.query_orderbook_hyperliquid
Error: Could not find module for exchange hyperliquid at bitmango.exchange.hyperliquid.query_orderbook_hyperliquid
Please ensure the exchange-specific query_orderbook module exists and is correctly named.

Stderr: 
Return Code: 1
```

### Hyperliquid - Query Order Book (Testnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Binance - Fetch Account Balance (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.binance.account_portfolio_binance
Loaded module: bitmango.exchange.binance.account_portfolio_binance
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Binance - Fetch Account Balance (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Binance - Fetch Open Positions (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.binance.account_portfolio_binance
Loaded module: bitmango.exchange.binance.account_portfolio_binance
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Binance - Fetch Open Positions (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Binance - Query Order Book (Mainnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: Debug: Attempting to import module: bitmango.exchange.binance.test_binance_market_query
Debug: Successfully imported module: bitmango.exchange.binance.test_binance_market_query
Debug: Attempting to get class: BinanceMarketQuery from module: bitmango.exchange.binance.test_binance_market_query
Debug: Successfully got class: BinanceMarketQuery
Error: API keys for binance are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Binance - Query Order Book (Testnet) - BTC/USDT
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

### Bitfinex - Fetch Account Balance (Mainnet)
- Status: FAIL
- Details:
```
Stdout: Attempting to import: bitmango.exchange.bitfinex.account_bitfinex
Loaded module: bitmango.exchange.bitfinex.account_bitfinex
Error: API keys for bitfinex are not configured in api_keys.py.

Stderr: 
Return Code: 1
```

### Bitfinex - Fetch Account Balance (Testnet)
- Status: FAIL
- Details:
```
Stdout: 
Stderr: usage: bitmango [-h] [--sandbox] [--daemonize]
                 {entry,cancel,stop,exit,account,query_order_book} ...
bitmango: error: unrecognized arguments: --sandbox

Return Code: 2
```

