# BitMango Global Deployment Map

This document serves as the master reference for the two-tier BitMango release strategy, mapping the relationship between the Open Source (Free) and Professional (Enterprise) editions.

---

## 1. Release Tier Matrix

| Feature | BitMango Community (Free) | BitMango Professional (Pro) |
| :--- | :--- | :--- |
| **Primary Tool** | `bitmango` (Binary) | **`bitmango-pro`** (Hardened Binary) |
| **Tech Stack** | Compiled Python | Python + Compiled Rust Engine |
| **Logic Layer** | CCXT / Open Source Plugins | Modular Rust Workspace (Hardened) |
| **Auditing** | None | Pro Audit Dashboard (`pro_audit.db`) |
| **Identity** | Local Vault | GitHub OAuth + HWID Fingerprinting |
| **Pricing** | Free (Open Source) | Licensed / Monthly Subscription |

---

## 2. Tier 1: BitMango Community (Free)
*Reference: @deploy-free.md*

The Community edition is the open-source core of BitMango. It is designed for individual developers and standard trading execution.

*   **Repository:** `bitmango-trade-cli-free` (Public).
*   **Distribution:** Available as both **Python Source** and a **Compiled Binary** (via Nuitka).
*   **Tech Stack:** 100% Python. **Does not contain any Rust code.**
*   **Exclusions:** All `bitmango-pro/` (Proprietary Rust Engine), `bitmango-dashboard/`, and `bitmango-validation-server/` components are stripped.
*   **License Stub:** `bitmango/license.py` is hardcoded to return `is_pro_enabled() = False`.

---

## 3. Tier 2: BitMango Professional (Hardened Binary)
*Reference: @deploy-pro.md*

The Professional edition is a hardened binary that combines the core Python logic with a high-performance Rust engine. It provides advanced execution, institutional auditing, and proprietary risk management features.

### 3.1 The Hardened Pro Core (`bitmango_pro_core`)
The Pro version uses a compiled Rust core to execute sensitive logic. This binary is **hardened**: every internal function call performs an automatic, non-bypassable "Secure Handshake."

*   **Internal Validation:** The Rust binary independently generates the Machine ID and validates the provided JWT token before executing any proprietary math.
*   **Black-Box Logic:** Proprietary features like `SmartLimit`, `SmartStops`, and `Kill-Switch` are physically locked inside machine code; they cannot be accessed or bypassed by modifying the Python wrapper.
*   **Heartbeat Sync:** Uses a 24-hour rolling heartbeat with a 48-hour total grace period before reverting to the Free tier.
*   **Machine Fingerprinting:** Generates an immutable hardware hash using System ID, CPUID, and Drive Serial components.

### 3.2 The BitMango Pro Dashboard
A central command center for professional operators:
*   **Identity:** Manage hardware resets and licenses via GitHub OAuth.
*   **Analytics:** Professional PnL visualization and behavioral analysis.
*   **Settings:** Manage global Kill-Switch and risk parameters remotely.

---

## 4. Repository & Build Map

### 4.1 Private Root (Development)
*   `bitmango/`: Core Python library used by both tiers.
*   `bitmango-pro/`: Modular Rust plugins and the `bitmango_pro_core` bridge.
*   `bitmango-dashboard/`: Axum-based web server for Pro analytics.

### 4.2 Build Workflow
1.  **Free:** Run `scripts/deploy/deploy_free_release.sh` -> Generates public Python-only repo.
2.  **Pro:** Run `scripts/build/build_pro.sh` -> Compiles Rust plugins into the **`bitmango-pro`** binary.

---
*Created: 2026-03-07 | Status: Verified Alpha Architecture*
