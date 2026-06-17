import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def management_movie():
    start_boxed_mode("OPEN ORDERS")
    display_message('info', "Fetching open orders for BTC-USDT...")
    display_message('success', "  ID: ord-99827342, Symbol: BTC/USDT, Side: BUY, Qty: 0.5")
    stop_boxed_mode()
    time.sleep(get_sleep_time(1))
    start_boxed_mode("CANCELLATION")
    display_message('action_start', "Cancelling order ord-99827342")
    time.sleep(get_sleep_time(0.8))
    display_message('action_stop', "Cancelling order ord-99827342", result_icon="✓")
    display_message('success', "Order cancelled successfully")
    stop_boxed_mode()

def exit_movie():
    start_boxed_mode("CLOSE")
    display_message('action_start', "Closing position for BTC-USDT")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Closing position for BTC-USDT", result_icon="✓")
    display_message('success', "Position liquidated at market price")
    stop_boxed_mode()

def cancel_all_movie():
    start_boxed_mode("CANCEL ALL")
    display_message('action_start', "Cancelling all active orders...")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Cancelled 5 orders across all pairs", result_icon="✓")
    display_message('info', "BTC/USDT: 2 orders cancelled")
    display_message('info', "ETH/USDT: 3 orders cancelled")
    stop_boxed_mode()

def close_all_movie():
    start_boxed_mode("CLOSE ALL")
    display_message('action_start', "Liquidating ALL positions immediately")
    time.sleep(get_sleep_time(1.5))
    display_message('action_stop', "Closed 2 active positions", result_icon="✓")
    display_message('success', "BTC/USDT Long: Closed @ Market")
    display_message('success', "SOL/USDT Short: Closed @ Market")
    stop_boxed_mode()

def report_movie():
    start_boxed_mode("REPORT")
    display_message('action_start', "Fetching trade history and calculating performance")
    time.sleep(get_sleep_time(1.5))
    display_message('action_stop', "Performance data compiled", result_icon="✓")
    
    display_message('info', f"{'Date':<25} | {'Symbol':<12} | {'Side':<5} | {'Price':<10} | {'Amount':<10} | {'Cost':<10} | {'Fee':<8}")
    display_message('info', "-" * 100)
    display_message('info', f"{'2026-02-19 10:00:00':<25} | {'BTC/USDT':<12} | {'BUY':<5} | {'69500.00':<10} | {'0.1000':<10} | {'6950.00':<10} | {'6.95':<8}")
    display_message('info', f"{'2026-02-19 11:30:00':<25} | {'BTC/USDT':<12} | {'SELL':<5} | {'74000.00':<10} | {'0.1000':<10} | {'7400.00':<10} | {'7.40':<8}")
    
    display_message('success', "Total Volume: $14,350.00", icon="📈")
    display_message('success', "Total Fees: $14.35", icon="💸")
    display_message('success', "Estimated Net PnL: +$435.65", icon="💰")
    stop_boxed_mode()

STEPS = {
    "open_orders": {
        "objective": "Order Management",
        "command_args": ["open_orders", "--pair", "btc-usdt"],
        "explanation": "Control your active instructions. List, verify, and cancel open orders with surgical precision. Never leave a ghost order behind.",
        "display_cmd": "bitmango open_orders --pair btc-usdt --exchange binance",
        "movie": management_movie,
        "use_case": "Prevent losing money: Identifying and cancelling 'stale' orders prevents unexpected fills when the market trend has changed.",
        "pro_tip": "If you see too many open orders, use 'cancel all' immediately to clear the deck and reset your strategy."
    },
    "close": {
        "objective": "Standardized Position Exit",
        "command_args": ["close", "--pair", "btc-usdt"],
        "explanation": "Swift and decisive liquidation. The 'close' command is a simplified primitive to exit any position at market price immediately.",
        "display_cmd": "bitmango close --pair btc-usdt --exchange binance",
        "movie": exit_movie,
        "use_case": "How it helps make money: Fast exit allows you to move capital into better performing assets quickly. \nPrevent losing money: Immediate exit is the only way to stop the bleeding in a trade that has failed its thesis.",
        "pro_tip": "Use 'close' instead of 'sell' when you want to be 100% sure you are exiting a position entirely rather than potentially opening a new short position."
    },
    "cancel_all": {
        "objective": "Mass Cancellation",
        "command_args": ["cancel", "all"],
        "explanation": "Clean slate protocol. Remove all open limit orders across the exchange instantly to prevent unwanted fills.",
        "display_cmd": "bitmango cancel all",
        "movie": cancel_all_movie,
        "use_case": "Prevent losing money: Essential when a major news event occurs; clearing all orders prevents 'old' strategies from triggering in a new, volatile market environment.",
        "pro_tip": "Cancel All is your first line of defense during a 'Flash Crash' if your automated bot stops functioning correctly."
    },
    "close_all": {
        "objective": "Emergency Liquidation",
        "command_args": ["close-all"],
        "explanation": "Panic button. Liquidate every single open position in your portfolio immediately at market price.",
        "display_cmd": "bitmango close-all",
        "movie": close_all_movie,
        "use_case": "Prevent losing money: Used for total portfolio risk management when the global market environment turns catastrophic.",
        "pro_tip": "In an absolute emergency, 'close-all' is the fastest way to return your entire portfolio to 'Cash' (USDT)."
    },
    "report": {
        "objective": "Institutional-Grade Reporting",
        "command_args": ["report", "--export", "screen", "--days", "1"],
        "explanation": "Institutional-grade performance analytics. Normalize your trade history into professional reports. Calculate volume and fees across any time period.",
        "display_cmd": "bitmango report --days 1 --export screen",
        "movie": report_movie,
        "use_case": "How it helps make money: Quantitative feedback on your 'Edge' allows you to bet larger on winning patterns and smaller on losing ones. \nPrevent losing money: Highlighting 'fee leakage' helps you choose more cost-effective exchanges or order types.",
        "pro_tip": "Run a daily report to ensure your trading fees are staying within your 'Risk Budget' for the month."
    }
}
