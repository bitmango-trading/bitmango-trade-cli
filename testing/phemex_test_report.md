# Phemex Testnet Definitive Verification Report

- **Date:** 2026-02-17
- **CCXT Version:** 4.5.38
- **Status:** Partially Functional (Spot only)

## Key Findings

### 1. The "Zombie" Matching Engine
The Phemex testnet matching engine appears to be selectively active. 
- **Spot Limit Orders:** **FUNCTIONAL.** Orders placed at the current Ask (for Buy) or current Bid (for Sell) fill correctly.
- **Spot Market Orders:** **NON-FUNCTIONAL.** Accepted by API but remain `Created`/`PendingNew` indefinitely.
- **Futures (Linear & Inverse):** **NON-FUNCTIONAL.** Both Limit and Market orders remain in `PendingNew` status regardless of price.

### 2. Mode Inconsistency Fixed
The `TE_ERR_INCONSISTENT_POS_MODE` (20004) error during cancellation and leverage adjustment was resolved by ensuring `posSide` (`Long`/`Short`) or `hedged: True` is explicitly passed in Hedge mode.

### 3. Account Type
The test account is a **Unified Trading Account** (`userMode: 1`). While this mode is designed for capital efficiency, the testnet implementation seems to have limited matching capabilities compared to production.

## Test Results Summary

| Test Category | Symbol | Result | Details |
|---|---|---|---|
| Load Markets | All | PASS | `bitmango markets` works. |
| Fetch Ticker | BTC/USDT | PASS | Active with volume. |
| Fetch Balance | USDT | PASS | Visible in Unified Account. |
| Spot Limit Buy | BTC/USDT | PASS | Filled when hitting Ask price. |
| Spot Market Buy | BTC/USDT | FAIL | Stuck in `open` status. |
| Futures Limit Buy | BTC/USDT:USDT | FAIL | Stuck in `PendingNew`. |
| Futures Market Buy | BTC/USDT:USDT | FAIL | Stuck in `PendingNew`. |
| Order Cancellation | BTC/USDT | PASS | Fixed with `posSide` parameter. |
| History | BTC/USDT | PASS | `bitmango history` works for Spot. |
| Funding Rate | BTC/USDT:USDT | PASS | `bitmango funding` works. |
| Set Leverage | BTC/USDT:USDT | PASS | `bitmango leverage` works (Hedge aware). |
| Set Margin Mode | BTC/USDT:USDT | PASS | `bitmango margin` works (Detected Isolated). |
| Transfer Funds | USDT | PASS | `bitmango transfer` works (Spot to Future). |
| Position Mode | BTC/USDT:USDT | PASS | `bitmango position-mode` works (private API). |

## Tool Improvements
- **Auto-Verification:** The `bitmango` tool now automatically verifies the outcome of every command:
    - **Entries/Exits:** Confirms fills for market orders and book entry for limit orders.
    - **Cancellations:** Confirms the book is cleared.
    - **Closures:** Confirms the position is actually zeroed.
    - **Stops:** Confirms the stop order is active in the book.
- **New Commands:** Added `leverage`, `margin`, `transfer`, `funding`, `markets`, `history`, `position-mode`, and `ledger` to the unified CLI.

## Missing Tool Functionality / Known Gaps
1. **Ledger/Activity:** Phemex does not support the standard CCXT `fetchLedger` method (confirmed via `ex.has['fetchLedger'] == None`), so the `ledger` command is non-functional for Phemex.
2. **Account Summary:** No single command to see a unified view of Spot + Futures balances and margin usage (currently separate).
3. **Hedge Mode Specifics:** `entry`/`exit` logic sometimes struggles with `posSide` requirement if the user doesn't specify `long`/`short` (Buy/Sell is ambiguous in Hedge mode). I have partially fixed this by defaulting based on position state where possible.

## Recommendation
- Use **Phemex Spot** for testing basic CLI order flow, balance updates, and cancellations.
- **Do not rely on Phemex for Futures testing.** The testnet matching engine for futures is essentially dead.
- Shift "Gold Standard" Futures testing to **OKX** or **Bitget** (modules already prepared).
