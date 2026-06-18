# Global Options

These options can be used with almost any command in the BitMango Trade CLI.

| Option | Shorthand | Description |
| :--- | :--- | :--- |
| `--exchange` | N/A | **Required.** Specifies the exchange to use (e.g., `binance`, `phemex`, `simulated`). |
| `--sandbox` | N/A | Enables Sandbox (Testnet) mode. Uses `_testnet` keys from `api_keys.py`. |
| `--market-type` | N/A | Switch between `spot` and `futures` markets. Default is `futures`. |
| `--verbose` | `-v` | Enables verbose output for more detail. |
| `--debug` | N/A | Enables high-level debug output (including full CCXT logs). |
| `--output` | `-o` | Sets output format: `human` (default) or `json` (for bots). |
| `--no-confirm` | N/A | Skips human confirmation prompts (auto-enabled in JSON mode). |
| `--no-color` | N/A | Disables ANSI color codes in the output. |

## Examples

### Using a specific exchange
```bash
./bitmango account --balance --exchange binance
```

### Running on Testnet
```bash
./bitmango buy --size 0.1 --pair BTC-USDT --exchange phemex --sandbox
```

### JSON Output for Bots
```bash
./bitmango account --balance --exchange simulated --output json
```
