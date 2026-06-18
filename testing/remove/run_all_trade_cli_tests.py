import os
import subprocess
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TRADE_CLI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bitmango'))
REPORT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test-results.md'))

EXCHANGES_TO_TEST = [
    'phemex',
    'bybit',
    'mexc',
    'hyperliquid',
    'binance',
    'bitfinex',
    'dydx',
]

# Helper function to run bitmango commands
def run_trade_cli_command(command_args, sandbox=False):
    full_command = [sys.executable, TRADE_CLI_PATH] + command_args
    if sandbox:
        full_command.append('--sandbox')

    print(f"Running command: {' '.join(full_command)}")
    process = subprocess.run(full_command, capture_output=True, text=True)
    return process.stdout, process.stderr, process.returncode

# Function to write results to report file
def write_report_header():
    with open(REPORT_FILE, 'w') as f:
        f.write(f"# Trade CLI Test Results ({os.path.basename(os.getcwd())})\n\n")
        f.write(f"Date: {os.popen('date').read().strip()}\n\n")
        f.write("## Test Summary\n\n")

def write_test_result(exchange, test_name, status, details=""):
    with open(REPORT_FILE, 'a') as f:
        f.write(f"### {exchange.capitalize()} - {test_name}\n")
        f.write(f"- Status: {status}\n")
        if details:
            f.write(f"- Details:\n```\n{details}\n```\n")
        f.write("\n")

def main():
    write_report_header()

    for exchange_name in EXCHANGES_TO_TEST:
        print(f"\n--- Running tests for {exchange_name.upper()} ---")

        # Test Case 1: Fetch Account Balance (Mainnet)
        test_name = f"Fetch Account Balance (Mainnet)"
        stdout, stderr, returncode = run_trade_cli_command(['account', '--exchange', exchange_name, '--balance'], sandbox=False)
        if returncode == 0 and "Error" not in stdout and "Error" not in stderr:
            write_test_result(exchange_name, test_name, "PASS", stdout)
        else:
            write_test_result(exchange_name, test_name, "FAIL", f"Stdout: {stdout}\nStderr: {stderr}\nReturn Code: {returncode}")

        # Test Case 2: Fetch Account Balance (Testnet)
        test_name = f"Fetch Account Balance (Testnet)"
        stdout, stderr, returncode = run_trade_cli_command(['account', '--exchange', exchange_name, '--balance'], sandbox=True)
        if returncode == 0 and "Error" not in stdout and "Error" not in stderr:
            write_test_result(exchange_name, test_name, "PASS", stdout)
        else:
            write_test_result(exchange_name, test_name, "FAIL", f"Stdout: {stdout}\nStderr: {stderr}\nReturn Code: {returncode}")

        # Test Case 3: Fetch Open Positions (Mainnet)
        test_name = f"Fetch Open Positions (Mainnet)"
        stdout, stderr, returncode = run_trade_cli_command(['account', '--exchange', exchange_name, '--positions'], sandbox=False)
        if returncode == 0 and "Error" not in stdout and "Error" not in stderr:
            write_test_result(exchange_name, test_name, "PASS", stdout)
        else:
            write_test_result(exchange_name, test_name, "FAIL", f"Stdout: {stdout}\nStderr: {stderr}\nReturn Code: {returncode}")

        # Test Case 4: Fetch Open Positions (Testnet)
        test_name = f"Fetch Open Positions (Testnet)"
        stdout, stderr, returncode = run_trade_cli_command(['account', '--exchange', exchange_name, '--positions'], sandbox=True)
        if returncode == 0 and "Error" not in stdout and "Error" not in stderr:
            write_test_result(exchange_name, test_name, "PASS", stdout)
        else:
            write_test_result(exchange_name, test_name, "FAIL", f"Stdout: {stdout}\nStderr: {stderr}\nReturn Code: {returncode}")

        # Test Case 5: Query Order Book (Mainnet) - BTC/USDT
        test_name = f"Query Order Book (Mainnet) - BTC/USDT"
        stdout, stderr, returncode = run_trade_cli_command(['query_order_book', '--exchange', exchange_name, '--pair', 'BTC-USDT'], sandbox=False)
        if returncode == 0 and "Error" not in stdout and "Error" not in stderr:
            write_test_result(exchange_name, test_name, "PASS", stdout)
        else:
            write_test_result(exchange_name, test_name, "FAIL", f"Stdout: {stdout}\nStderr: {stderr}\nReturn Code: {returncode}")

        # Test Case 6: Query Order Book (Testnet) - BTC/USDT
        test_name = f"Query Order Book (Testnet) - BTC/USDT"
        stdout, stderr, returncode = run_trade_cli_command(['query_order_book', '--exchange', exchange_name, '--pair', 'BTC-USDT'], sandbox=True)
        if returncode == 0 and "Error" not in stdout and "Error" not in stderr:
            write_test_result(exchange_name, test_name, "PASS", stdout)
        else:
            write_test_result(exchange_name, test_name, "FAIL", f"Stdout: {stdout}\nStderr: {stderr}\nReturn Code: {returncode}")

        # TODO: Add more test cases for entry, exit, stop, cancel commands
        # These will require careful handling of order placement and cancellation to avoid leaving open orders.
        # For now, focus on read-only operations.

    print("\n--- All tests completed. Check test-results.md for details ---")

if __name__ == "__main__":
    main()
