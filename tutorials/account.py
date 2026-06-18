import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def balance_movie():
    start_boxed_mode("ACCOUNT BALANCE")
    display_message('action_start', "Fetching balances from Binance")
    time.sleep(get_sleep_time(0.8))
    display_message('action_stop', "Fetching balances from Binance", result_icon="✓")
    display_message('success', "Binance Spot Balance:")
    display_message('success', "  USDT: 12,450.25")
    display_message('success', "  BTC: 0.1000")
    stop_boxed_mode()

def positions_movie():
    start_boxed_mode("ACCOUNT POSITIONS")
    display_message('action_start', "Fetching active positions from Binance Futures")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Fetching active positions from Binance Futures", result_icon="✓")
    display_message('info', "Open Positions on Binance:")
    display_message('success', "  Symbol: BTC/USDT:USDT")
    display_message('success', "  Side: LONG")
    display_message('success', "  Size: 0.1 BTC")
    display_message('success', "  Entry Price: 69,500.00")
    display_message('success', "  Unrealized PnL: +$45.20")
    display_message('info', "-" * 30)
    stop_boxed_mode()

def history_movie():
    start_boxed_mode("ORDER HISTORY")
    display_message('action_start', "Fetching recent trade history")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Retrieved 50 recent trades", result_icon="✓")
    display_message('info', f"{'Date':<20} | {'Pair':<10} | {'Side':<5} | {'Price':<10} | {'Qty':<10}")
    display_message('info', "-" * 65)
    display_message('success', f"{'2026-02-19 10:00':<20} | {'BTC/USDT':<10} | {'BUY':<5} | {'69500.00':<10} | {'0.1000':<10}")
    display_message('success', f"{'2026-02-19 09:30':<20} | {'BTC/USDT':<10} | {'SELL':<5} | {'71200.00':<10} | {'0.0500':<10}")
    display_message('success', f"{'2026-02-18 15:45':<20} | {'ETH/USDT':<10} | {'BUY':<5} | {'3850.00':<10} | {'1.5000':<10}")
    stop_boxed_mode()

def ledger_movie():
    start_boxed_mode("ACCOUNT LEDGER")
    display_message('action_start', "Fetching ledger transactions")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Retrieved recent ledger entries", result_icon="✓")
    display_message('info', f"{'Date':<20} | {'Asset':<5} | {'Type':<12} | {'Amount':<10}")
    display_message('info', "-" * 55)
    display_message('success', f"{'2026-02-19 10:00':<20} | {'USDT':<5} | {'TRADE_FEE':<12} | {'-2.50':<10}")
    display_message('success', f"{'2026-02-19 10:00':<20} | {'BTC':<5} | {'TRADE_BUY':<12} | {'+0.1000':<10}")
    display_message('success', f"{'2026-02-18 08:00':<20} | {'USDT':<5} | {'FUNDING':<12} | {'-0.45':<10}")
    stop_boxed_mode()

def transfer_movie():
    start_boxed_mode("TRANSFER")
    display_message('action_start', "Initiating transfer: Spot -> Futures")
    display_message('info', "Asset: USDT | Amount: 5000.00")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Transfer successful: Spot -> Futures (5000 USDT)", result_icon="✓")
    stop_boxed_mode()

def trades_movie():
    start_boxed_mode("TRADES (FILLS)")
    display_message('action_start', "Fetching execution trades")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Retrieved recent fills", result_icon="✓")
    display_message('info', f"{'Date':<20} | {'Pair':<10} | {'Side':<5} | {'Price':<10} | {'Qty':<10}")
    display_message('info', "-" * 65)
    display_message('success', f"{'2026-02-19 10:00':<20} | {'BTC/USDT':<10} | {'BUY':<5} | {'69502.50':<10} | {'0.1000':<10}")
    display_message('success', f"{'2026-02-19 09:30':<20} | {'BTC/USDT':<10} | {'SELL':<5} | {'71205.10':<10} | {'0.0500':<10}")
    stop_boxed_mode()

STEPS = {
    "account": {
        "objective": "Account & Portfolio Auditing",
        "command_args": ["account", "--balance"],
        "explanation": "Maintain total awareness. Quickly audit your sub-account balances and active positions across the exchange. BitMango normalizes data into a single, clean view.",
        "display_cmd": "bitmango account --balance --exchange binance",
        "movie": balance_movie,
        "use_case": "Prevent losing money: Constant awareness of your 'Free Margin' prevents accidental liquidation due to lack of collateral for existing futures positions.",
        "pro_tip": "Run 'account --balance' before every major entry to ensure your 'Free Margin' is sufficient for the trade size."
    },
    "positions": {
        "objective": "Position Monitoring",
        "command_args": ["account", "--positions"],
        "explanation": "Track your profitability in real-time. See exactly which positions are open and their current entry prices. BitMango calculates unrealized PnL automatically.",
        "display_cmd": "bitmango account --positions --exchange binance",
        "movie": positions_movie,
        "use_case": "How it helps make money: Real-time PnL monitoring allows you to strategically exit winning trades at the peak of their momentum. \nPrevent losing money: Identifying 'toxic' positions early allows for proactive risk reduction.",
        "pro_tip": "Use 'account --positions' in combination with 'close' for ultra-fast profit taking when targets are hit."
    },
    "history": {
        "objective": "Trade History",
        "command_args": ["history", "--pair", "btc-usdt"],
        "explanation": "Review your past execution performance. The 'history' command pulls your recent filled orders directly from the exchange api.",
        "display_cmd": "bitmango history --pair btc-usdt",
        "movie": history_movie,
        "use_case": "How it helps make money: Analyzing your past winners and losers helps refine your strategy. \nPrevent losing money: Identifying patterns of poor execution (e.g. over-trading) helps you develop discipline.",
        "pro_tip": "Export your history to CSV regularly to build a long-term 'Trading Journal' for deep quantitative analysis."
    },
    "trades": {
        "objective": "Execution Audit",
        "command_args": ["trades"],
        "explanation": "Audit every single execution. Unlike 'history' which shows orders, 'trades' shows the actual fills, including the exact price paid and fees incurred for each chunk of your order.",
        "display_cmd": "bitmango trades --pair btc-usdt",
        "movie": trades_movie,
        "use_case": "How it helps make money: Verify that you are receiving the best possible execution price from the exchange's matching engine. \nPrevent losing money: High execution fees can destroy a profitable strategy. Use 'trades' to monitor your 'Effective Fee' per trade.",
        "pro_tip": "Compare 'trades' price to 'history' limit price to see how much positive or negative slippage you are experiencing."
    },
    "ledger": {
        "objective": "Ledger Audit",
        "command_args": ["ledger"],
        "explanation": "Deep dive into your account movements. The 'ledger' command shows all balance changes, including deposits, withdrawals, fees, and funding payments.",
        "display_cmd": "bitmango ledger --exchange binance",
        "movie": ledger_movie,
        "use_case": "Prevent losing money: Funding rates can drain an account over time. Checking the ledger helps you identify high-cost 'Carry' positions that should be closed.",
        "pro_tip": "Check the ledger after every large trade to verify that the exchange applied the correct fee tier to your account."
    },
    "transfer": {
        "objective": "Internal Transfers",
        "command_args": ["transfer", "--currency", "USDT", "--amount", "5000", "--from-account", "spot", "--to-account", "futures"],
        "explanation": "Move capital instantly between your sub-accounts (e.g., Spot to Futures) without leaving the terminal.",
        "display_cmd": "bitmango transfer --currency USDT --amount 5000 --from-account spot --to-account futures",
        "movie": transfer_movie,
        "use_case": "Prevent losing money: Quickly moving funds from Spot to Futures can provide a 'Margin Buffer' during extreme market flash crashes, preventing liquidation.",
        "pro_tip": "Automate transfers using a simple cron job and the JSON output mode to maintain a fixed 'Operating Capital' in your futures account."
    }
}
