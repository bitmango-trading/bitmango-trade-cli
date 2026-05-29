# Binance Testnet Technical Specification

## Core Requirement: Isolated Test Environments

Binance maintains entirely separate environments for its Spot and Futures testnets. This isolation means that API keys, authentication methods, and endpoints are **not interchangeable**.

### 1. Key Features & Differences

| Feature | Spot Testnet | Futures (UM) Testnet |
| :--- | :--- | :--- |
| **Portal URL** | [testnet.binance.vision](https://testnet.binance.vision) | [testnet.binancefuture.com](https://testnet.binancefuture.com) |
| **Authentication** | GitHub Login | Binance Account Login |
| **API Base URL** | `https://testnet.binance.vision/api` | `https://demo-fapi.binance.com` |
| **WebSocket URL** | `wss://testnet.binance.vision/ws` | `wss://fstream.binancefuture.com` |
| **Asset Faucet** | Managed via the Portal | Managed via the Dashboard |
| **Data Persistence** | Frequently Reset | Persistent within the test account |

---

### 2. Implementation Technical Specs

#### A. Binance Spot Testnet
- **Key Generation**: Requires a GitHub account. One key pair is generated at a time.
- **HMAC_SHA256**: Uses standard HMAC-SHA256 signing for authenticated requests.
- **Limited Scope**: Primarily supports `/api/v3/*` endpoints. Most `/sapi/v1/*` (Wallet, Staking, etc.) endpoints are **not supported** in the testnet environment.
- **Liquidations/Liquidity**: Very low liquidity compared to the live environment.

#### B. Binance Futures Testnet
- **Key Generation**: Requires creating a separate account on the Futures Testnet portal (can be linked to a real Binance account).
- **Endpoint Structure**: All endpoints typically follow the `/fapi/v1/*` or `/dapi/v1/*` patterns.
- **Position Modes**: Supports both "One-Way" and "Hedge" modes, which must be configured via the portal before API use or through the `POST /fapi/v1/positionSide/dual` endpoint.
- **Distinct USDT Faucet**: USDT must be requested from the testnet dashboard faucet for use as margin.

---

### 3. Practical Implementation Guidelines for `bitmango`

1.  **Vault Storage**: When configuring `binance_testnet`, the user must be prompted or informed whether they are providing a **Spot** or **Futures** testnet key.
2.  **Configuration Logic**: The internal `bitmango/exchange/binance` module must dynamically switch its `ccxt` base URLs based on whether it is targeting Spot or Futures:
    -   `target='spot'`, `sandbox=True` → `https://testnet.binance.vision`
    -   `target='futures'`, `sandbox=True` → `https://testnet.binancefuture.com` (or `demo-fapi.binance.com`)
3.  **Error Handling**: If a Spot key is used on a Futures endpoint, the API will return a `401 Unauthorized` or an `API-key format invalid` error. The `bitmango` error handler should explicitly mention the "Bespoke Testnet Setup" as a potential cause for Binance authentication failures in sandbox mode.

---

### 4. Setup Steps Summary

- **Spot**: Go to `testnet.binance.vision` → Login with GitHub → Generate Key → Use `testnet.binance.vision` endpoints.
- **Futures**: Go to `testnet.binancefuture.com` → Create/Link Account → API Management → Create Key → Use `testnet.binancefuture.com` endpoints.
