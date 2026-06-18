# Hardware Keys Setup Guide

BitMango Pro uses hardware-bound licensing to ensure maximum security for institutional trading. Your **Hardware Key** is a unique fingerprint generated from your terminal's hardware components.

## 🛠️ How to find your Hardware Key

To retrieve your Hardware Key, you can use the `bitmango` (v2.4.0+).

### Using the CLI (Recommended)

Run the following command in your terminal:

```bash
bitmango hwid
```

**Output Example:**
```text
🆔 YOUR HARDWARE KEY: 0515e3b4443ae922b8c8d8f1e2a3b4c5
```

---

## 💎 How to register your Key

1.  **Login** to the BitMango Pro Dashboard.
2.  Navigate to **Settings** -> **Hardware Keys**.
3.  **Paste** your Hardware Key into the input field.
4.  Click **Update Hardware Key**.

Once registered, your `bitmango` will immediately unlock professional features, including:
- Smart Orders & Advanced Execution
- Real-time Institutional Analytics
- Automated Risk Management Breach Protection

---

## ⚠️ Important Security Notes

- **One Key per Account:** Your license is bound to a single terminal. Changing your Hardware Key in the dashboard will immediately de-authorize your previous machine.
- **Privacy:** The Hardware Key is a one-way cryptographic hash of your system's hardware UUIDs. It cannot be used to identify your personal data or track your location.
- **Verification:** The CLI validates your key against the BitMango secure ledger on every institutional trade. Ensure your terminal has an active internet connection for the initial validation.

---

*Need help? Contact institutional support or join the community Discord.*
