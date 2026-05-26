# BitMango Deployment & Release Plan

This document outlines the strategy for deploying BitMango in two distinct tiers: **Free (Open Source)** and **Professional (Enterprise)**.

## 1. Repository Structure
*   **`bitmango-free/` (Public):** The Open Source Core. Contains the Python engine and basic plugins.
*   **`bitmango-pro/` (Private):** The Hardened Engine. Contains the **Modular Rust Workspace** for Pro features and proprietary math.
*   **`bitmango-validation-server/` (Private):** High-performance Rust/Axum API for license management.

## 2. Pro Feature Matrix (Compiled Rust)
The following Pro features are implemented as independent, high-performance Rust crates:
1.  **SmartStops:** Advanced trailing stop-loss algorithms.
2.  **Pro Indicators:** High-frequency technical indicator calculations.
3.  **Accounting:** Proprietary PnL, Ledger, and Portfolio audit logic.
4.  **Pro Orders:** Iceberg, TWAP, and slice-execution algorithms.
5.  **Kill Switch:** Low-latency risk management and exposure protection.

## 3. Deployment Workflow (`deploy.sh`)
The deployment script automates the creation of the public repository:
1.  **Sanitization:** Deletes all `bitmango-pro/` and `bitmango-validation-server/` folders.
2.  **Logic Strip:** Ensures no Pro-tier Python "glue" files remain in the Free version.
3.  **Leak Audit:** Runs a cryptographic and text-based audit to confirm the Free version has zero Pro-logic dependencies.

## 4. Validation System (Pro Only)
BitMango Pro requires an active internet connection for daily validation.
*   **Server:** `validation.bitmango.win` (Rust/Axum/SQLx).
*   **Auth:** Hardware ID (Machine fingerprinting) + Signed JWT Heartbeat.
*   **Grace Period:** 24-hour window if the server is unreachable.
*   **Trial System:** Automatic **7-day free trial** for any new Machine ID.

## 5. Security Mandates
*   **No Pro-Logic in Free Core:** The core engine is designed to fail gracefully if the Pro binary is missing.
*   **Binary Integrity:** The CLI verifies the hash of the `bitmango-pro` binary against official GitHub releases.
*   **One License per Machine:** Licenses are hard-locked to hardware identifiers.

---
*Updated on 2026-03-06 for Modular Rust Plugin Phase.*
