# Getting Started

## 🚀 One-Step Installation

BitMango includes a local installer that sets up global shims and a managed environment.

1.  **Run the installer:**
    ```bash
    ./scripts/utils/install.sh
    ```
2.  **Verify:**
    ```bash
    bitmango --help
    ```

This installs BitMango to `~/.bitmango` and adds shims to `~/.local/bin`.

## 🔐 Secure API Key Configuration

While you can use `api_keys.py`, we recommend using the **BitMango Vault** for encrypted credential storage.

### 1. Initialize the Vault
```bash
./bitmango-vault --setup
```
Follow the prompts to set a master password and optional TOTP (2FA). This only needs to be run once.

### 2. Create a Session
To avoid repeated password prompts during an active trading session, create a temporary session:
```bash
./bitmango-vault --session
```

### 3. Store Your Keys
```bash
./bitmango-vault --add --exchange binance
```

### 4. Usage
When you run `bitmango`, it will automatically check for an active session. If none exists, it will prompt for your master password or TOTP code to unlock the keys.

---

## 🛠️ Sandbox (Testnet) Mode
To practice without risking capital, use the `--sandbox` flag. This will automatically look for `_testnet` keys in your vault or `api_keys.py`.
