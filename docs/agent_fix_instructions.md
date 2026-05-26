# Final Fix Instructions for Bitmango CLI (Proactive Lock & Indicators)

## Context
The `bitmango` CLI tool now correctly returns **pure JSON** to `stdout` by embedding logs into the JSON object. This is a major improvement for automation. Symbol normalization and indicator flags (`--rsi`, `--ema`) are also implemented.

## Objective
Fix the `bitmango` CLI tool to ensure non-trading commands (like `ohlcv`) are NOT blocked by risk/trading suspensions, and verify the indicator JSON schema.

---

## ISSUE 1: Proactive Risk Lock (Global Blocker)
A "Proactive Risk Breach" is currently blocking ALL commands, including read-only ones like `ohlcv`.

### Reproduction
```bash
bitmango ohlcv --pair "BTC/USD" --exchange phemex --sandbox --limit 1 --rsi 14 -o json
```

### Actual Output
```json
{
  "error": "TRADING PERMANENTLY SUSPENDED: PROACTIVE LOCK: RISK BREACH...",
  "status": "permission_denied",
  ...
}
```

### Requirement
- Read-only/Data commands like `ohlcv`, `ticker`, and `markets` should **NEVER** be blocked by trading suspensions or risk breaches.
- Provide a way to "Reset" or "Acknowledge" the suspension via the CLI (e.g., `bitmango kill-switch --reset`).

---

## ISSUE 2: Verify Indicator JSON Schema
Once the lock is bypassed, verify that `--rsi 14` correctly includes the RSI values in the OHLCV JSON response.

### Expected Schema Example (One of these):
1.  **Appended to Candle Array**: `[timestamp, open, high, low, close, volume, rsi]`
2.  **Key-Value Object**: `{"timestamp": ..., "close": ..., "indicators": {"rsi": 45.2}}`

---

## Verification Checklist for Agent
- [ ] `bitmango ohlcv` returns data even if a trading suspension is active.
- [ ] `bitmango buy --pair "BTC/USD"` uses a safe default (like $100) instead of triggering a $65k risk breach on the first run.
- [ ] The JSON output remains pure and parseable via `jq`.

## Reference Log
Refer to `bitmango_issues.log` for raw traces of the risk lock.
