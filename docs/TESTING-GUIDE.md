# Testing Guide for BitMango Trade CLI

This guide outlines the robust testing methodology for the BitMango Trade CLI, prioritizing local simulation and network resilience before moving to real exchange environments.

## 🏆 The "Gold Standard" Strategy

We follow a three-tiered testing hierarchy to ensure maximum reliability and safety:

### 1. Local Simulation (Primary)
The cornerstone of our testing is the **FastAPI Simulator**. It provides a high-fidelity, 100% controllable mock of an exchange API. This allows developers to:
*   Verify all CLI commands (`entry`, `exit`, `account`, `leverage`, etc.) without risking real funds or relying on flaky testnets.
*   Test edge cases and error handling.
*   Run tests instantly without network latency.

### 2. Network Stress Testing (Chaos Injection)
Using the simulator's **Chaos Middleware**, we verify the CLI's resilience against:
*   High latency (4s+ spikes).
*   Intermittent 5xx server errors.
*   Random connection dropouts.
Our `_request_with_retry` logic is validated here using exponential backoff.

### 3. Manual & Real Testnet Validation (Secondary)
Once a feature is verified locally, it is tested against real exchange testnets (e.g., Phemex Testnet). This confirms that our exchange-specific templates correctly map to real-world API behaviors and quirks.

---

## 🚀 How to Run Tests

### Standard Automated Suite
Use the **Master Test Runner** to execute the comprehensive suite. It automatically manages the simulator lifecycle.

```bash
./.venv/bin/python testing/run_all_tests.py --exchange simulated
```

To run against a real testnet (e.g., Phemex):
```bash
./.venv/bin/python testing/run_all_tests.py --exchange phemex --environment sandbox
```

### Network Resilience (Stress) Tests
Verify that the tool can survive a "broken" network environment.

```bash
./.venv/bin/python testing/network_stress_suite.py
```

### Manual Verification
For interactive, step-by-step human verification on real exchanges:

```bash
./.venv/bin/python testing/run_manual_tests.py --exchange <name> --environment sandbox
```

---

## 📁 Infrastructure Overview

*   **`testing/simulator/`**: A standalone FastAPI service that mimics a real exchange.
*   **`testing/comprehensive_test_suite.py`**: The "full-sweep" test covering every CLI command.
*   **`testing/run_all_tests.py`**: The entry point that orchestrates environment setup and suite execution.
*   **`testing/network_stress_suite.py`**: Programmatically injects chaos into the simulator to test resilience.

---

## ⚠️ Safety Protections

The test suite includes a **Live Mode Protection** mechanism. When running against a real exchange in `live` mode, all "destructive" commands (placing orders, closing positions, cancelling orders) are automatically skipped unless the `--force-live` flag is explicitly provided.

**Example of a safe live run (informational only):**
```bash
./.venv/bin/python testing/run_all_tests.py --exchange binance --environment live
```
