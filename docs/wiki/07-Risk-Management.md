# Hardened Risk Management

In the world of high-leverage crypto trading, **Risk is the only thing you can truly control.** BitMango provides the tools to harden your portfolio against catastrophic "tail risk."

---

## 1. Universal Kill Switch (PRO Binary)
*Defeating the Risk of Ruin*

The Kill Switch is a specialized background monitor integrated into BitMango Professional binaries. It watches your total account equity and enforces strict safety constraints.

### ⚔️ The Nuclear Option: Manual Panic
If you see something wrong in the market or your bot's behavior, you can trigger an immediate, global shutdown.
- **Action:** Cancels all open orders, market-closes all positions, and **permanently suspends trading** by locking the vault.
- **Command:**
  ```bash
  bitmango kill-switch panic
  ```

### 🛡️ Proactive Risk Lock
BitMango doesn't just wait for you to panic. It proactively monitors every command for a **RISK BREACH**. If a breach is detected, the system triggers an emergency shutdown automatically.

### 📏 Technical Mandates (Enforced)
- **10s Data Freshness:** BitMango will reject any market data (tickers, order books) older than 10 seconds. Trading on stale data is a technical failure.
- **5% Price Deviation:** Limit orders placed more than 5% away from the current mark price are rejected to prevent "fat-finger" errors or flash-crash slippage.
- **$100 Order Cap (Default):** BitMango starts with a tight **$100 safety cap** per individual order to protect users from accidental large exposure.

#### 🔓 How to increase the Order Cap
If you are ready to trade larger sizes, you can override the safety cap by setting the `BITMANGO_MAX_ORDER_USD` environment variable in your shell or `.env` file:

```bash
# Set cap to $50,000 USD
export BITMANGO_MAX_ORDER_USD=50000
```

### 📈 Equity Monitoring
Set a global `--max-loss` threshold to protect your principal. 
- **Total Protection:** If your net unrealized loss hits your threshold (e.g. -$500), BitMango fires the emergency protocol.

---

## 2. Dynamic Leverage Control
*Freeing Up Capital, Not Increasing Risk*

### ⚔️ The Execution Edge
Use the `leverage` command to scale your capital efficiency. Professional traders use high leverage not to gamble with larger positions, but to **free up USDT collateral** for other opportunities while maintaining the same position size.

**Command:**
```bash
./bitmango leverage --pair BTC-USDT --leverage 20 --exchange phemex
```

---

## 3. Isolated vs. Cross Margin
*Containment Protocols*

### ⚔️ The Execution Edge
- **Isolated Margin:** Your loss is restricted to the specific collateral assigned to that trade. Use this for experimental or high-risk "Sniper" entries.
- **Cross Margin:** Your entire account balance acts as collateral. Use this for your core, low-leverage "Trend Following" positions to avoid liquidation during brief volatility spikes.

**Command:**
```bash
./bitmango margin --pair BTC-USDT --mode isolated --exchange binance
```

---

## 4. Position Mode (Hedge vs. One-Way)
*Sophisticated Delta Neutrality*

### ⚔️ The Execution Edge
Hedge mode allows you to hold both a LONG and a SHORT position on the same pair simultaneously. This is crucial for:
- **Scalping the Range:** Capture profits from both the top and bottom of a consolidation zone without closing your core long-term position.
- **Delta Hedging:** Protect your spot holdings by opening a short futures position during a market correction.

**Command:**
```bash
./bitmango position-mode --pair BTC-USDT --mode hedge --exchange phemex
```
