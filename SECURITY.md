# Security Policy

## Supported Versions

| Version | Supported |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of our users' assets extremely seriously. If you discover a vulnerability, please report it immediately.

**DO NOT** open a public issue.

Instead, please email **security@bitmango.win** with the subject line `[VULNERABILITY] - <Short Description>`.

We will acknowledge your report within 24 hours and provide an estimated timeline for a fix.

## Security Best Practices

### 1. API Key Management
*   **Permissions:** Always grant the minimum necessary permissions to your API keys. For this CLI, only **"Trade"** and **"Read"** (or "Data") permissions are required. **NEVER** grant "Withdraw" permissions.
*   **IP Whitelisting:** Wherever possible, whitelist your specific IP address in the exchange's API settings.
*   **Storage:** Store your `api_keys.py` file with strict permissions (`chmod 600 api_keys.py`).
*   **Environment Variables:** For enhanced security, use environment variables instead of the `api_keys.py` file:
    *   `BINANCE_API_KEY`, `BINANCE_SECRET`
    *   `PHEMEX_API_KEY`, `PHEMEX_SECRET`

### 2. Plugin Security
*   **Verified Plugins:** Only use plugins from the official BitMango repository or verified partners.
*   **Review Code:** If using a community plugin, audit the source code before running it.
*   **Pro License:** The Pro binary runs in a hardened environment. Ensure your license is valid to access these security features.

### 3. Updates
*   Keep your CLI updated to the latest version to ensure you have the latest security patches and exchange compatibility fixes.
