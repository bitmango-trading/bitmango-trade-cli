import unittest.mock
import argparse
import subprocess
import sys
import os
import re

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_dir)
from bitmango_free.exchange.base_exchange import BaseExchange

# Use relative path for dev env
TRADE_CLI_PATH = os.path.join(base_dir, "bitmango")

def run_trade_cli_command(command_args, exchange, environment, no_confirm_flag=True):
    # Use sys.executable to ensure we use the same venv
    # The command should come before the global arguments in this CLI's structure
    # bitmango <command> --exchange <exchange> ...
    
    cmd = command_args[0]
    rest = command_args[1:]
    
    full_command = [sys.executable, TRADE_CLI_PATH, cmd, "--exchange", exchange]
    if environment == "sandbox":
        full_command.append("--sandbox")
    
    if exchange == "simulated":
        full_command += ["--market-type", "spot"]
    else:
        full_command += ["--market-type", "futures"]

    full_command.extend(rest)
    if no_confirm_flag:
        full_command.append("--no-confirm")
    
    # Always use --no-color for easier parsing in tests
    full_command.append("--no-color")

    print(f"Running command: {' '.join(full_command)}")
    result = subprocess.run(full_command, capture_output=True, text=True)
    return result

def test_account_balance(exchange, environment):
    test_name = f"Account Balance ({exchange}, {environment})"
    print(f"--- Running Test: {test_name} ---")
    command_args = ["account", "--balance"]
    result = run_trade_cli_command(command_args, exchange, environment)
    if result.returncode == 0 and "balance" in result.stdout.lower():
        print(f"PASS: {test_name}")
        return True
    print(f"FAIL: {test_name}\nStdout: {result.stdout}\nStderr: {result.stderr}")
    return False

def test_markets(exchange, environment):
    test_name = f"Markets List ({exchange}, {environment})"
    print(f"--- Running Test: {test_name} ---")
    result = run_trade_cli_command(["markets"], exchange, environment)
    if result.returncode == 0 and "markets" in result.stdout.lower():
        print(f"PASS: {test_name}")
        return True
    print(f"FAIL: {test_name}")
    return False

def test_funding(exchange, environment):
    test_name = f"Funding Rate ({exchange}, {environment})"
    print(f"--- Running Test: {test_name} ---")
    result = run_trade_cli_command(["funding", "--pair", "BTC-USDT"], exchange, environment)
    if result.returncode == 0 and "funding" in result.stdout.lower():
        print(f"PASS: {test_name}")
        return True
    print(f"FAIL: {test_name}")
    return False

def test_leverage(exchange, environment):
    test_name = f"Set Leverage ({exchange}, {environment})"
    print(f"--- Running Test: {test_name} ---")
    if exchange == "simulated":
        print(f"SKIP: {test_name} - Skipping leverage for simulated spot.")
        return True
    result = run_trade_cli_command(["leverage", "--pair", "BTC-USDT", "--leverage", "5"], exchange, environment)
    if result.returncode == 0 and "success" in result.stdout.lower():
        print(f"PASS: {test_name}")
        return True
    print(f"FAIL: {test_name}")
    return False

def test_entry_market_buy(exchange, environment):
    test_name = f"Entry Market Buy ({exchange}, {environment})"
    print(f"--- Running Test: {test_name} ---")
    if environment == "live": return True
    command_args = ["entry", "--pair", "BTC-USDT", "--direction", "buy", "--size", "0.001", "--order-type", "market"]
    result = run_trade_cli_command(command_args, exchange, environment)
    if result.returncode == 0 and ("executed" in result.stdout.lower() or "success" in result.stdout.lower()):
        print(f"PASS: {test_name}")
        return True
    print(f"FAIL: {test_name}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Run standardized exchange tests.")
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--environment", choices=["live", "sandbox"], required=True)
    args = parser.parse_args()

    exchange = args.exchange.lower()
    environment = args.environment.lower()

    print(f"Starting tests for {exchange} in {environment} environment...")

    tests = [
        test_account_balance,
        test_markets,
        test_funding,
        test_leverage,
        test_entry_market_buy,
    ]

    results = {}
    for test_func in tests:
        results[test_func.__name__] = "PASS" if test_func(exchange, environment) else "FAIL"
    
    print("\n--- Test Summary ---")
    for test_name, status in results.items():
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    main()
