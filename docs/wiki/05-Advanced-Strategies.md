# Advanced Strategies: The Professional Playbook (PRO Binary)

BitMango Trade CLI isn't just a wrapper—it's a tactical execution engine. This playbook outlines how to use the advanced logic integrated into our **Professional Edition binaries** to gain a measurable edge over retail traders.

---

## 1. TWAP Orders (PRO Binary)
*Neutralizing the Slippage Tax*

The Time-Weighted Average Price (TWAP) algorithm executes large positions by slicing them into smaller chunks over a specific duration.

### ⚔️ The Execution Edge
Use the `twap` command to randomized your entry over several minutes or hours.
- **Stealth:** Your true size is never visible on the Tape.
- **Precision:** Randomized intervals prevent predatory bots from timing your next chunk.

**Command:**
```bash
bitmango twap --pair BTC-USDT --direction buy --total-size 1.0 --duration 10 --chunks 5 --exchange binance
```

---

## 2. Iceberg Orders (PRO Binary)
*Hiding Your Hand*

Iceberg orders keep the majority of your order hidden, only exposing a small "visible" portion to the order book.

### ⚔️ The Execution Edge
Use the `iceberg` command to sit at a specific price level without alerting other traders to your true liquidity.
- **Order Book Integrity:** Prevents the "wall" effect that scares price away from your entry.
- **Automated Refills:** BitMango automatically places the next visible slice as soon as the current one is filled.

**Command:**
```bash
bitmango iceberg --pair BTC-USDT --direction buy --total-size 5.0 --visible-size 0.1 --price 68500 --exchange phemex
```

---

## 3. CLI-Side Trailing Stops (PRO)
*Automated Profit Harvesting for All Exchanges*

While some exchanges offer native trailing stops, BitMango's CLI-side Trailing Stop brings this logic to **every supported exchange**, regardless of their native capabilities.

### ⚔️ The Execution Edge
Set a 1% `--stop-type trailing`. 
- **Universal Support:** Use trailing stops on exchanges that don't natively support them.
- **Dynamic Floor:** If price hits a new peak, your stop automatically rises to lock in more profit.
- **Hands-Off:** Eliminates the emotional struggle of "when to exit."

**Command:**
```bash
./bitmango stop --stop-type trailing --callback-percentage 0.01 --size 1.0 --pair BTC-USDT --exchange phemex
```

---

## 3. Ghost Stops (PRO)
*Defeating the Stop-Hunters*

Ghost stops reside only in your local CLI memory. They are invisible to the exchange and other participants.

### 🎯 The Scenario
Price is consolidating near a major support level. You know there is a "cluster" of retail stop-losses just below that level. Market makers often push price briefly into that cluster to trigger liquidations (Stop-Hunting) before the real move starts.

### ⚔️ The Execution Edge
Use `--stop-type ghost`. 
- **Invisibility:** You do not appear in the exchange's "Stop Order" data.
- **Survival:** While retail stops are being "hunted" and triggered, your Ghost stop waits for a *sustained* price breach before firing.
- **Stealth Exit:** Only sends a market order to the exchange at the exact second of execution.

**Command:**
```bash
./bitmango stop --stop-type ghost --stop-price 59450 --size 1.0 --pair BTC-USDT --exchange binance
```

---

## 4. Smart Stops (PRO)
*Optimized Emergency Exits*

*Note: Smart Stop logic is currently exchange-specific (Optimized for Phemex).*

### ⚔️ The Execution Edge
Combines a native exchange-side safety stop with an aggressive local "Smart Limit" exit. It attempts to exit your position using limit orders at the best possible price, only falling back to a market exit if volatility becomes extreme.
- **Slippage Reduction:** Saves up to 50% of exit slippage vs a standard market stop.
- **Hard Floor:** Always maintains a native stop-loss as a backup if your internet fails.

**Command:**
```bash
./bitmango stop --smart-stop --stop-price 58000 --size 1.0 --pair BTC-USDT --exchange phemex
```
