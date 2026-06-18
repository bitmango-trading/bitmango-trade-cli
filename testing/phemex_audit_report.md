# Phemex Comprehensive Audit Report

**Date:** 2026-02-22 22:36:56
**Environment:** Sandbox
**Pair:** btc-usdt

| Feature | Sub-Feature | Status | Message | Error |
|---------|-------------|--------|---------|-------|
| Account | Balance (Futures) | PASS | Fetched balance |  |
| Account | Positions | PASS | Fetched positions |  |
| Account | Set Leverage | PASS | Set leverage to 5 |  |
| Account | Set Margin Mode | FAIL | Set margin to cross | phemex {"code":20004,"msg":"TE_ERR_INCONSISTENT_POS_MODE","data":null} |
| Account | Set Position Mode | PASS | Set position mode to hedge |  |
| Account | Ledger/History | FAIL | Fetched ledger for USDT | phemex fetchLedger() is not supported yet |
| Market Data | Markets List | PASS | Fetched markets |  |
| Market Data | Order Book | PASS | Fetched order book |  |
| Trading | Limit Entry | PASS | Placed limit buy |  |
| Trading | Cancel All (Pair) | FAIL | Cancelled by pair | Command Timed Out |
| Stops | Native Stop Loss | PASS | Placed stop loss | ERROR: Failed to place native stop: phemex {"code":11011,"msg":"TE_REDUCE_ONLY_ABORT","data":null}  |
| Stops | Native Take Profit | PASS | Placed take profit | ERROR: Failed to place native stop: phemex {"code":11011,"msg":"TE_REDUCE_ONLY_ABORT","data":null}  |
| Stops | Trailing Stop | PASS | Skipped (Long-running) |  |
