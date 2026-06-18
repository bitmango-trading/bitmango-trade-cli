import subprocess
import os
import sys
import argparse

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

TRADE_CLI_PATH = os.path.join(project_root, "bitmango")
MANUAL_TEST_RESULTS_FILE = os.path.join(project_root, "testing/manual_test_results.md")

def run_trade_cli_command(command_args, exchange, environment, no_confirm_flag=False):
    full_command = [TRADE_CLI_PATH]
    full_command.extend(command_args)
    if environment == "sandbox":
        full_command.append("--sandbox")
    full_command.extend(["--exchange", exchange])
    if no_confirm_flag:
        full_command.append("--no-confirm")

    print(f"\nExecuting command: {' '.join(full_command)}")
    result = subprocess.run(full_command, capture_output=True, text=True)
    print("--- Command Output ---")
    print(result.stdout)
    if result.stderr:
        print("--- Command Error (Stderr) ---")
        print(result.stderr)
    print("----------------------")
    return result

def record_manual_test_result(test_name, exchange, environment, status, details="", human_comment=""):
    with open(MANUAL_TEST_RESULTS_FILE, "a") as f:
        f.write(f"## Manual Test Result: {test_name} ({exchange.capitalize()} - {environment.capitalize()})\n")
        f.write(f"- **Status:** {status}\n")
        if details:
            f.write(f"- **Details:** {details}\n")
        if human_comment: # Add human comment if provided
            f.write(f"- **Human Comment:** {human_comment}\n")
        f.write(f"- **Timestamp:** {os.path.getmtime(MANUAL_TEST_RESULTS_FILE)}\n") # Placeholder for actual timestamp
        f.write("\n---\n\n")

def get_human_verification(prompt):
    while True:
        response = input(f"\n{prompt} (y/N): ").lower()
        if response == 'y':
            return True, "" # Return True and an empty comment
        elif response == 'n':
            comment = input("Please provide a brief comment (optional): ").strip()
            return False, comment # Return False and the comment
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def manual_test_close_all_positions(exchange, environment):
    test_name = "Close All Positions"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Step 1: Attempt to close all open positions for spot
    print("\n**Step 1: Attempting to close all Spot positions**")
    # This assumes 'exit all' command exists and works for positions
    command_args_exit_spot = ["exit", "all", "--market-type", "spot"]
    result_exit_spot = run_trade_cli_command(command_args_exit_spot, exchange, environment, no_confirm_flag=True)

    if result_exit_spot.returncode != 0:
        print(f"WARNING: Could not automatically close all Spot positions. Please manually close them.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Could not automatically close all Spot positions.")

    # Step 2: Attempt to close all open positions for futures
    print("\n**Step 2: Attempting to close all Futures positions**")
    command_args_exit_futures = ["exit", "all", "--market-type", "futures"]
    result_exit_futures = run_trade_cli_command(command_args_exit_futures, exchange, environment, no_confirm_flag=True)

    if result_exit_futures.returncode != 0:
        print(f"WARNING: Could not automatically close all Futures positions. Please manually close them.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Could not automatically close all Futures positions.")

    # Step 3: Human Verification: Verify no open positions
    print("\n**Step 3: Human Verification: Verify no open positions**")
    print("Please check your positions on the exchange for both Spot and Futures markets. There should be no open positions.")
    no_open_positions, comment_positions = get_human_verification("Are there no open positions for Spot and Futures?")
    if not no_open_positions:
        print(f"Manual Test '{test_name}' FAILED: Open positions still exist.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Open positions still exist.", human_comment=comment_positions)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_cancel_all_orders(exchange, environment):
    test_name = "Cancel All Orders"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Step 1: Attempt to cancel all open orders for spot
    print("\n**Step 1: Attempting to cancel all Spot orders**")
    command_args_cancel_spot = ["cancel", "all", "--market-type", "spot"]
    result_cancel_spot = run_trade_cli_command(command_args_cancel_spot, exchange, environment, no_confirm_flag=True)

    if result_cancel_spot.returncode != 0:
        print(f"WARNING: Could not automatically cancel all Spot orders. Please manually cancel them.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Could not automatically cancel all Spot orders.")

    # Step 2: Attempt to cancel all open orders for futures
    print("\n**Step 2: Attempting to cancel all Futures orders**")
    command_args_cancel_futures = ["cancel", "all", "--market-type", "futures"]
    result_cancel_futures = run_trade_cli_command(command_args_cancel_futures, exchange, environment, no_confirm_flag=True)

    if result_cancel_futures.returncode != 0:
        print(f"WARNING: Could not automatically cancel all Futures orders. Please manually cancel them.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Could not automatically cancel all Futures orders.")

    # Step 3: Human Verification: Verify no open orders
    print("\n**Step 3: Human Verification: Verify no open orders**")
    print("Please check your open orders on the exchange for both Spot and Futures markets. There should be no open orders.")
    no_open_orders, comment_orders = get_human_verification("Are there no open orders for Spot and Futures?")
    if not no_open_orders:
        print(f"Manual Test '{test_name}' FAILED: Open orders still exist.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Open orders still exist.", human_comment=comment_orders)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def perform_cleanup(exchange, environment):
    print("--- Performing Automated Cleanup (Close Positions & Cancel Orders) ---")
    close_positions_passed = manual_test_close_all_positions(exchange, environment)
    cancel_orders_passed = manual_test_cancel_all_orders(exchange, environment)
    if close_positions_passed and cancel_orders_passed:
        print("--- Automated Cleanup Completed Successfully ---")
        return True
    else:
        print("--- Automated Cleanup Failed. Please manually clean up your account. ---")
        return False


def manual_test_account_balance(exchange, environment):
    test_name = "Account Balance Check"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")
    print("\n**Step 1: Manual Account Zeroing**")
    print("Please manually zero out your account on the Phemex testnet for this exchange.")
    print("Ensure there are no open positions, no active limit orders, and no active conditional orders for **both Spot and Futures markets**.")
    confirmed_zeroed, comment = get_human_verification("Have you manually zeroed the account for both Spot and Futures?")
    if not confirmed_zeroed:
        print("Manual account zeroing not confirmed. Skipping test.")
        record_manual_test_result(test_name, exchange, environment, "SKIPPED", "Manual account zeroing not confirmed.", human_comment=comment)
        return False

    # Test Spot Balance
    print("\n**Step 2: Running bitmango account --balance for Spot Market**")
    command_args_spot = ["account", "--balance", "--market-type", "spot"]
    result_spot = run_trade_cli_command(command_args_spot, exchange, environment)

    print("\n**Step 3: Human Verification for Spot Balance**")
    print("Please compare the 'Command Output' above with your actual **Spot balance** on the exchange.")
    matches_spot, comment = get_human_verification("Does the bitmango output match your manually observed Spot balance?")
    if not matches_spot:
        print(f"Manual Test '{test_name}' FAILED for Spot Balance.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Spot balance output did not match manually observed balance.", human_comment=comment)
        return False

    # Test Futures Balance
    print("\n**Step 4: Running bitmango account --balance for Futures Market**")
    command_args_futures = ["account", "--balance", "--market-type", "futures"]
    result_futures = run_trade_cli_command(command_args_futures, exchange, environment)

    print("\n**Step 5: Human Verification for Futures Balance**")
    print("Please compare the 'Command Output' above with your actual **Futures balance** on the exchange.")
    matches_futures, comment = get_human_verification("Does the bitmango output match your manually observed Futures balance?")
    if not matches_futures:
        print(f"Manual Test '{test_name}' FAILED for Futures Balance.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Futures balance output did not match manually observed balance.", human_comment=comment)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_market_buy_order(exchange, environment):
    test_name = "Market Buy Order & Position Check"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Pre-condition: Check balance
    print("\n**Step 0: Checking Account Balance**")
    command_args_balance = ["account", "--balance", "--market-type", "spot"]
    result_balance = run_trade_cli_command(command_args_balance, exchange, environment)
    print("\n**Human Verification for Balance**")
    print("Please ensure you have sufficient funds to execute the test order.")
    has_funds, comment_funds = get_human_verification("Do you have sufficient funds (e.g., > 1 USDT)?")
    if not has_funds:
        print(f"Manual Test '{test_name}' SKIPPED due to insufficient funds.")
        record_manual_test_result(test_name, exchange, environment, "SKIPPED", "Insufficient funds.", human_comment=comment_funds)
        return False

    # Action: Place a market buy order
    print("\n**Step 1: Placing a Market Buy Order for BTC-USDT (Futures)**")

    # We need to ensure the pair is correct for the exchange.
    # For Phemex, it's BTC/USDT.
    pair = "BTC-USDT"
    size = 0.001 # Very small size for testing

    command_args_entry = ["entry", "--pair", pair, "--direction", "buy", "--size", str(size), "--order-type", "market", "--market-type", "futures"]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Market Buy Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Market Buy Order placement failed.")
        return False

    # Expected Final State: One open long position, no open orders.
    print("\n**Step 2: Verifying Open Positions**")
    command_args_positions = ["account", "--positions", "--market-type", "futures"] 
    result_positions = run_trade_cli_command(command_args_positions, exchange, environment)

    print("\n**Step 3: Human Verification for Position**")
    print(f"Please compare the 'Command Output' above with your actual **open positions** on the exchange for {pair}.")
    print(f"You should see one long position of size {size}.")
    matches_position, comment_position = get_human_verification("Does the bitmango output match your manually observed position?")
    if not matches_position:
        print(f"Manual Test '{test_name}' FAILED at Step 3: Position verification failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Position verification failed.", human_comment=comment_position)
        return False

    print("\n**Step 4: Verifying No Open Orders**")
    command_args_open_orders = ["open_orders", "--pair", pair, "--market-type", "futures"]
    result_open_orders = run_trade_cli_command(command_args_open_orders, exchange, environment)

    print("\n**Step 5: Human Verification for No Open Orders**")
    print(f"Please compare the 'Command Output' above with your actual **open orders** on the exchange for {pair}.")
    print("You should see no open orders (as it was a market order).")
    matches_no_orders, comment_no_orders = get_human_verification("Does the bitmango output confirm no open orders?")
    if not matches_no_orders:
        print(f"Manual Test '{test_name}' FAILED at Step 5: Open orders verification failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Open orders verification failed.", human_comment=comment_no_orders)
        return False

    # Cleanup: Close the position
    print("\n**Step 6: Cleaning up - Closing the position**")
    command_args_exit = ["exit", "specific", "--pair", pair, "--direction", "sell", "--size", str(size), "--order-type", "market", "--market-type", "futures"]
    result_exit = run_trade_cli_command(command_args_exit, exchange, environment, no_confirm_flag=True)

    if result_exit.returncode != 0 or "order executed" not in result_exit.stdout.lower():
        print(f"WARNING: Cleanup failed for '{test_name}'. Could not close position. Please manually close the position.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Cleanup failed: Could not close position.")
        # Do not return False here, as the test itself might have passed, only cleanup failed.

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_limit_order_placement_and_cancellation(exchange, environment):
    test_name = "Limit Order Placement & Cancellation"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    pair = "BTC-USDT"
    size = 0.001
    price = 10000 # A low price to ensure it doesn't fill immediately

    # Step 1: Place a limit buy order
    print(f"\n**Step 1: Placing a Limit Buy Order for {pair} at {price}**")
    command_args_entry = ["entry", "--pair", pair, "--direction", "buy", "--size", str(size), "--order-type", "limit", "--market-type", "spot", "--price", str(price)]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Limit Buy Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Limit Buy Order placement failed.")
        return False

    # Step 2: Human Verification: Verify the order is open
    print("\n**Step 2: Human Verification for Open Order**")
    print(f"Please check your open orders on the exchange. You should see a limit buy order for {pair} at {price}.")
    order_is_open, comment_open = get_human_verification(f"Is the limit buy order for {pair} open on the exchange?")
    if not order_is_open:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Limit buy order not found or not open.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Limit buy order not found or not open.", human_comment=comment_open)
        return False

    # Step 3: Cancel the order
    print(f"\n**Step 3: Cancelling the order for {pair}**")
    command_args_cancel = ["cancel", "all", "--pair", pair, "--market-type", "spot"]
    result_cancel = run_trade_cli_command(command_args_cancel, exchange, environment, no_confirm_flag=True)

    if result_cancel.returncode != 0 or "order cancelled" not in result_cancel.stdout.lower():
        print(f"WARNING: Cleanup failed for '{test_name}'. Could not cancel the order. Please manually cancel the order.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Cleanup failed: Could not cancel the order.")
        # Do not return False here, as the test itself might have passed, only cleanup failed.

    # Step 4: Human Verification: Verify the order is no longer open
    print("\n**Step 4: Human Verification for No Open Order**")
    print(f"Please check your open orders on the exchange. The limit buy order for {pair} should no longer be open.")
    order_is_closed, comment_closed = get_human_verification(f"Is the limit buy order for {pair} no longer open on the exchange?")
    if not order_is_closed:
        print(f"Manual Test '{test_name}' FAILED at Step 4: Order still open after cancellation.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Order still open after cancellation.", human_comment=comment_closed)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_stop_order_placement_and_triggering(exchange, environment):
    test_name = "Stop Order Placement & Triggering"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    pair = "BTC-USDT"
    size = 0.001
    stop_price = 15000 # A price that can be triggered manually

    # Step 1: Place a stop market order
    print(f"\n**Step 1: Placing a Stop Market Order for {pair} at stop price {stop_price}**")
    # Using 'native-stop' command
    command_args_entry = ["native-stop", "--pair", pair, "--direction", "buy", "--size", str(size), "--stop-price", str(stop_price), "--market-type", "spot"]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Stop Market Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Stop Market Order placement failed.")
        return False

    # Step 2: Human Verification: Verify the order is open
    print("\n**Step 2: Human Verification for Open Stop Order**")
    print(f"Please check your open orders on the exchange. You should see a stop market order for {pair} at stop price {stop_price}.")
    order_is_open, comment_open = get_human_verification(f"Is the stop market order for {pair} open on the exchange?")
    if not order_is_open:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Stop market order not found or not open.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Stop market order not found or not open.", human_comment=comment_open)
        return False

    # Step 3: Human Action: Trigger the stop order
    print(f"\n**Step 3: Human Action: Trigger the stop order for {pair}**")
    print(f"Please manually move the market price of {pair} on the exchange to trigger the stop order (e.g., above {stop_price}).")
    order_triggered, comment_triggered = get_human_verification(f"Has the stop order for {pair} been triggered and executed on the exchange?")
    if not order_triggered:
        print(f"Manual Test '{test_name}' FAILED at Step 3: Stop order not triggered or executed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Stop order not triggered or executed.", human_comment=comment_triggered)
        return False

    # Step 4: Human Verification: Verify the order is no longer open and position is opened/closed
    print("\n**Step 4: Human Verification for No Open Order and Position Change**")
    print(f"Please check your open orders and positions on the exchange. The stop order for {pair} should no longer be open, and your position should reflect the execution of the stop order.")
    position_changed, comment_position = get_human_verification(f"Is the stop order for {pair} no longer open and has your position changed accordingly?")
    if not position_changed:
        print(f"Manual Test '{test_name}' FAILED at Step 4: Order still open or position not changed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Order still open or position not changed.", human_comment=comment_position)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_trailing_stop_order_placement_and_triggering(exchange, environment):
    test_name = "Trailing Stop Order Placement & Triggering"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    pair = "BTC-USDT"
    size = 0.001
    # For trailing stop, we need a trail value, not a fixed stop price
    # Assuming 'stop' command with a 'trailing' argument or similar
    # The actual implementation in bitmango might differ.
    trail_value = 100 # Example trail value in USD

    # Step 1: Place a trailing stop order
    print(f"\n**Step 1: Placing a Trailing Stop Order for {pair} with callback 1%**")
    # Using 'trailing-stop' command
    command_args_entry = ["trailing-stop", "--pair", pair, "--direction", "buy", "--size", str(size), "--callback-percentage", "0.01", "--market-type", "spot"]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Trailing Stop Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Trailing Stop Order placement failed.")
        return False

    # Step 2: Human Verification: Verify the order is open
    print("\n**Step 2: Human Verification for Open Trailing Stop Order**")
    print(f"Please check your open orders on the exchange. You should see a trailing stop order for {pair}.")
    order_is_open, comment_open = get_human_verification(f"Is the trailing stop order for {pair} open on the exchange?")
    if not order_is_open:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Trailing stop order not found or not open.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Trailing stop order not found or not open.", human_comment=comment_open)
        return False

    # Step 3: Human Action: Trigger the trailing stop order
    print(f"\n**Step 3: Human Action: Trigger the trailing stop order for {pair}**")
    print(f"Please manually move the market price of {pair} on the exchange to trigger the trailing stop order.")
    order_triggered, comment_triggered = get_human_verification(f"Has the trailing stop order for {pair} been triggered and executed on the exchange?")
    if not order_triggered:
        print(f"Manual Test '{test_name}' FAILED at Step 3: Trailing stop order not triggered or executed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Trailing stop order not triggered or executed.", human_comment=comment_triggered)
        return False

    # Step 4: Human Verification: Verify the order is no longer open and position is opened/closed
    print("\n**Step 4: Human Verification for No Open Order and Position Change**")
    print(f"Please check your open orders and positions on the exchange. The trailing stop order for {pair} should no longer be open, and your position should reflect the execution of the trailing stop order.")
    position_changed, comment_position = get_human_verification(f"Is the trailing stop order for {pair} no longer open and has your position changed accordingly?")
    if not position_changed:
        print(f"Manual Test '{test_name}' FAILED at Step 4: Order still open or position not changed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Order still open or position not changed.", human_comment=comment_position)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True




def manual_test_account_positions(exchange, environment):
    test_name = "Account Positions Check"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Action: Run bitmango account --positions
    print("\n**Step 1: Running bitmango account --positions**")
    command_args = ["account", "--positions", "--market-type", "futures"] # Assuming futures positions for now
    result = run_trade_cli_command(command_args, exchange, environment)

    # Human Verification
    print("\n**Step 2: Human Verification for Positions**")
    print("Please compare the 'Command Output' above with your actual **open positions** on the exchange.")
    matches_positions, comment = get_human_verification("Does the bitmango output match your manually observed open positions?")
    if not matches_positions:
        print(f"Manual Test '{test_name}' FAILED: Positions output did not match manually observed positions.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Positions output did not match manually observed positions.", human_comment=comment)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_open_orders(exchange, environment):
    test_name = "Open Orders Check"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Action: Run bitmango open_orders
    print("\n**Step 1: Running bitmango open_orders**")
    command_args = ["open_orders", "--pair", "BTC-USDT"] # Assuming BTC-USDT for now
    result = run_trade_cli_command(command_args, exchange, environment)

    # Human Verification
    print("\n**Step 2: Human Verification for Open Orders**")
    print("Please compare the 'Command Output' above with your actual **open orders** on the exchange.")
    matches_orders, comment = get_human_verification("Does the bitmango output match your manually observed open orders?")
    if not matches_orders:
        print(f"Manual Test '{test_name}' FAILED: Open orders output did not match manually observed orders.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Open orders output did not match manually observed orders.", human_comment=comment)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_futures_limit_buy(exchange, environment):
    test_name = "Futures Limit Buy Order"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Pre-condition: Ensure no open orders for BTC-USDT
    print("\n**Step 0: Ensuring no open orders for BTC-USDT**")
    command_args_open_orders = ["open_orders", "--pair", "BTC-USDT"]
    result_open_orders = run_trade_cli_command(command_args_open_orders, exchange, environment)
    print("Please ensure there are no open orders for BTC-USDT on the exchange.")
    no_open_orders, comment_open_orders = get_human_verification("Are there no open orders for BTC-USDT?")
    if not no_open_orders:
        print(f"Manual Test '{test_name}' SKIPPED due to existing open orders.")
        record_manual_test_result(test_name, exchange, environment, "SKIPPED", "Existing open orders for BTC-USDT.", human_comment=comment_open_orders)
        return False

    # Action: Place a futures limit buy order
    print("\n**Step 1: Placing a Futures Limit Buy Order for BTC-USDT**")
    pair = "BTC-USDT"
    size = 0.001 # Small size for testing
    price = 10000 # A low price to ensure it doesn't fill immediately

    command_args_entry = ["entry", "--pair", pair, "--direction", "buy", "--size", str(size), "--order-type", "limit", "--market-type", "futures", "--price", str(price)]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Futures Limit Buy Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Futures Limit Buy Order placement failed.")
        return False

    # Human Verification: Verify the order is open
    print("\n**Step 2: Human Verification for Open Order**")
    print("Please check your open orders on the exchange. You should see a limit buy order for BTC-USDT at 10000.")
    order_is_open, comment_open = get_human_verification("Is the limit buy order for BTC-USDT open on the exchange?")
    if not order_is_open:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Limit buy order not found or not open.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Limit buy order not found or not open.", human_comment=comment_open)
        return False

    # Cleanup: Cancel the order
    print("\n**Step 3: Cleaning up - Cancelling the order**")
    command_args_cancel = ["cancel", "specific", "--pair", pair, "--market-type", "futures", "--direction", "buy", "--size", str(size)] # Need to be more specific for cancel specific
    # For now, let's assume cancel all works for cleanup
    command_args_cancel_all = ["cancel", "all", "--pair", pair, "--market-type", "futures"]
    result_cancel = run_trade_cli_command(command_args_cancel_all, exchange, environment, no_confirm_flag=True)

    if result_cancel.returncode != 0 or "order cancelled" not in result_cancel.stdout.lower():
        print(f"WARNING: Cleanup failed for '{test_name}'. Could not cancel the order. Please manually cancel the order.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Cleanup failed: Could not cancel the order.")
        # Do not return False here, as the test itself might have passed, only cleanup failed.

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_futures_market_sell(exchange, environment):
    test_name = "Futures Market Sell Order"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Pre-condition: Ensure an open long position for BTC-USDT
    print("\n**Step 0: Ensuring an open long position for BTC-USDT**")
    # This is tricky for a manual test. User needs to manually open a position.
    print("Please manually open a long position for BTC-USDT on the exchange (e.g., buy 0.001 BTC).")
    has_position, comment_position = get_human_verification("Do you have an open long position for BTC-USDT?")
    if not has_position:
        print(f"Manual Test '{test_name}' SKIPPED due to no open long position.")
        record_manual_test_result(test_name, exchange, environment, "SKIPPED", "No open long position for BTC-USDT.", human_comment=comment_position)
        return False

    # Action: Place a futures market sell order
    print("\n**Step 1: Placing a Futures Market Sell Order for BTC-USDT**")
    pair = "BTC-USDT"
    size = 0.001 # Size to sell

    command_args_entry = ["entry", "--pair", pair, "--direction", "sell", "--size", str(size), "--order-type", "market", "--market-type", "futures"]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Futures Market Sell Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Futures Market Sell Order placement failed.")
        return False

    # Human Verification: Verify the position is closed or reduced
    print("\n**Step 2: Human Verification for Position**")
    print("Please check your positions on the exchange. Your long position for BTC-USDT should be closed or reduced.")
    position_closed, comment_closed = get_human_verification("Is your long position for BTC-USDT closed or reduced on the exchange?")
    if not position_closed:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Position not closed or reduced.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Position not closed or reduced.", human_comment=comment_closed)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_futures_limit_sell(exchange, environment):
    test_name = "Futures Limit Sell Order"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Pre-condition: Ensure an open long position for BTC-USDT
    print("\n**Step 0: Ensuring an open long position for BTC-USDT**")
    # This is tricky for a manual test. User needs to manually open a position.
    print("Please manually open a long position for BTC-USDT on the exchange (e.g., buy 0.001 BTC).")
    has_position, comment_position = get_human_verification("Do you have an open long position for BTC-USDT?")
    if not has_position:
        print(f"Manual Test '{test_name}' SKIPPED due to no open long position.")
        record_manual_test_result(test_name, exchange, environment, "SKIPPED", "No open long position for BTC-USDT.", human_comment=comment_position)
        return False

    # Action: Place a futures limit sell order
    print("\n**Step 1: Placing a Futures Limit Sell Order for BTC-USDT**")
    pair = "BTC-USDT"
    size = 0.001 # Size to sell
    price = 50000 # A high price to ensure it doesn't fill immediately

    command_args_entry = ["entry", "--pair", pair, "--direction", "sell", "--size", str(size), "--order-type", "limit", "--market-type", "futures", "--price", str(price)]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Futures Limit Sell Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Futures Limit Sell Order placement failed.")
        return False

    # Human Verification: Verify the order is open
    print("\n**Step 2: Human Verification for Open Order**")
    print("Please check your open orders on the exchange. You should see a limit sell order for BTC-USDT at 50000.")
    order_is_open, comment_open = get_human_verification("Is the limit sell order for BTC-USDT open on the exchange?")
    if not order_is_open:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Limit sell order not found or not open.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Limit sell order not found or not open.", human_comment=comment_open)
        return False

    # Cleanup: Cancel the order
    print("\n**Step 3: Cleaning up - Cancelling the order**")
    command_args_cancel_all = ["cancel", "all", "--pair", pair, "--market-type", "futures"]
    result_cancel = run_trade_cli_command(command_args_cancel_all, exchange, environment, no_confirm_flag=True)

    if result_cancel.returncode != 0 or "order cancelled" not in result_cancel.stdout.lower():
        print(f"WARNING: Cleanup failed for '{test_name}'. Could not cancel the order. Please manually cancel the order.")
        record_manual_test_result(test_name, exchange, environment, "WARNING", "Cleanup failed: Could not cancel the order.")
        # Do not return False here, as the test itself might have passed, only cleanup failed.

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def manual_test_spot_market_sell(exchange, environment):
    test_name = "Spot Market Sell Order"
    print(f"\n=== Running Manual Test: {test_name} for {exchange.capitalize()} ({environment.capitalize()}) ===")

    # Pre-condition: Ensure an open long position for BTC-USDT
    print("\n**Step 0: Ensuring an open long position for BTC-USDT**")
    # This is tricky for a manual test. User needs to manually open a position.
    print("Please manually open a long position for BTC-USDT on the exchange (e.g., buy 0.001 BTC).")
    has_position, comment_position = get_human_verification("Do you have an open long position for BTC-USDT?")
    if not has_position:
        print(f"Manual Test '{test_name}' SKIPPED due to no open long position.")
        record_manual_test_result(test_name, exchange, environment, "SKIPPED", "No open long position for BTC-USDT.", human_comment=comment_position)
        return False

    # Action: Place a spot market sell order
    print("\n**Step 1: Placing a Spot Market Sell Order for BTC-USDT**")
    pair = "BTC-USDT"
    size = 0.001 # Size to sell

    command_args_entry = ["entry", "--pair", pair, "--direction", "sell", "--size", str(size), "--order-type", "market", "--market-type", "spot"]
    result_entry = run_trade_cli_command(command_args_entry, exchange, environment, no_confirm_flag=True)

    if result_entry.returncode != 0 or "order executed" not in result_entry.stdout.lower():
        print(f"Manual Test '{test_name}' FAILED at Step 1: Spot Market Sell Order placement failed.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Spot Market Sell Order placement failed.")
        return False

    # Human Verification: Verify the position is closed or reduced
    print("\n**Step 2: Human Verification for Position**")
    print("Please check your positions on the exchange. Your long position for BTC-USDT should be closed or reduced.")
    position_closed, comment_closed = get_human_verification("Is your long position for BTC-USDT closed or reduced on the exchange?")
    if not position_closed:
        print(f"Manual Test '{test_name}' FAILED at Step 2: Position not closed or reduced.")
        record_manual_test_result(test_name, exchange, environment, "FAIL", "Position not closed or reduced.", human_comment=comment_closed)
        return False

    print(f"Manual Test '{test_name}' PASSED.")
    record_manual_test_result(test_name, exchange, environment, "PASS")
    return True

def main():
    parser = argparse.ArgumentParser(description="Run manual tests for bitmango functions.")
    parser.add_argument("--exchange", required=True, help="The exchange to test (e.g., phemex).")
    parser.add_argument("--environment", choices=["live", "sandbox"], default="sandbox", help="The environment to test (live or sandbox).")
    parser.add_argument("--test-name", help="Specific test to run (substring match).")
    
    args = parser.parse_args()

    exchange = args.exchange.lower()
    environment = args.environment.lower()
    target_test = args.test_name.lower() if args.test_name else None

    print(f"\n--- Starting Manual Test Suite for {exchange.capitalize()} ({environment.capitalize()}) ---")

    test_results = {}

    # Run initial cleanup tests
    initial_cleanup_passed = perform_cleanup(exchange, environment)
    test_results["Initial Cleanup (Close Positions & Cancel Orders)"] = initial_cleanup_passed

    if not initial_cleanup_passed:
        print(f"\n--- Manual Test Suite for {exchange.capitalize()} ({environment.capitalize()}) FAILED at Initial Cleanup. Please resolve the issue before retrying. ---")
        sys.exit(1) # Exit if initial cleanup fails, as subsequent tests rely on a clean state

    # Run other manual tests sequentially, with cleanup before each if initial cleanup passed
    test_functions = [
        ("Account Balance Check", manual_test_account_balance),
        ("Market Buy Order & Position Check", manual_test_market_buy_order),
        ("Limit Order Placement & Cancellation", manual_test_limit_order_placement_and_cancellation),
        ("Stop Order Placement & Triggering", manual_test_stop_order_placement_and_triggering),
        ("Trailing Stop Order Placement & Triggering", manual_test_trailing_stop_order_placement_and_triggering),
        ("Account Positions Check", manual_test_account_positions),
        ("Open Orders Check", manual_test_open_orders),
        ("Futures Limit Buy Order", manual_test_futures_limit_buy),
        ("Futures Market Sell Order", manual_test_futures_market_sell),
        ("Futures Limit Sell Order", manual_test_futures_limit_sell),
        ("Spot Market Sell Order", manual_test_spot_market_sell),
    ]

    for test_name, test_func in test_functions:
        if target_test and target_test not in test_name.lower():
            continue

        # Perform cleanup before each test if initial cleanup was successful
        if initial_cleanup_passed:
            print(f"\n--- Running Cleanup before {test_name} ---")
            cleanup_before_test_passed = perform_cleanup(exchange, environment)
            if not cleanup_before_test_passed:
                print(f"WARNING: Cleanup before {test_name} failed. Proceeding with test, but state might not be clean.")
        
        test_results[test_name] = test_func(exchange, environment)

    failed_tests = [name for name, result in test_results.items() if result is False]
    skipped_tests = [name for name, result in test_results.items() if result is None]
    passed_tests = [name for name, result in test_results.items() if result is True]

    print("\n" + "="*50)
    print("      MANUAL TEST SUITE SUMMARY")
    print("="*50)
    print(f"Exchange:    {exchange.capitalize()}")
    print(f"Environment: {environment.capitalize()}")
    print("-"*50)
    print(f"PASSED:  {len(passed_tests)}")
    print(f"FAILED:  {len(failed_tests)}")
    # We don't explicitly return None yet, but manual_test functions can be updated if needed.
    # Currently result is True/False.
    print("-"*50)
    
    if failed_tests:
        print("\nFAILED TESTS:")
        for t in failed_tests:
            print(f"  [❌] {t}")
            
    if passed_tests:
        print("\nPASSED TESTS:")
        for t in passed_tests:
            print(f"  [✓] {t}")

    if not failed_tests:
        print(f"\n--- Manual Test Suite for {exchange.capitalize()} ({environment.capitalize()}) Completed Successfully ---")
    else:
        print(f"\n--- Manual Test Suite for {exchange.capitalize()} ({environment.capitalize()}) FAILED ---")




if __name__ == "__main__":
    # Clear previous manual test results before starting a new run
    if os.path.exists(MANUAL_TEST_RESULTS_FILE):
        os.remove(MANUAL_TEST_RESULTS_FILE)
    main()
