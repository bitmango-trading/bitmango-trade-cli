import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def market_data_movie():
    start_boxed_mode("MARKETS")
    display_message('info', "Loading available markets for Binance")
    display_message('success', "  BTC/USDT")
    display_message('success', "  ETH/USDT")
    display_message('success', "  SOL/USDT")
    display_message('info', "  ... and 245 more.")
    stop_boxed_mode()
    time.sleep(get_sleep_time(1))
    start_boxed_mode("FUNDING")
    display_message('action_start', "Fetching funding rate for BTC-USDT")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Current Funding Rate: 0.0001", result_icon="✓")
    stop_boxed_mode()

def order_book_movie():
    start_boxed_mode("ORDER BOOK")
    display_message('action_start', "Fetching L2 Order Book for BTC-USDT")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Order Book Depth: 20", result_icon="✓")
    display_message('info', f"{'Price (USDT)':<15} | {'Size (BTC)':<12} | {'Side':<6}")
    display_message('info', "-" * 40)
    display_message('error', f"{'70150.50':<15} | {'2.500':<12} | {'ASK':<6}")
    display_message('error', f"{'70125.00':<15} | {'0.850':<12} | {'ASK':<6}")
    display_message('success', f"{'70100.00':<15} | {'1.200':<12} | {'BID':<6}")
    display_message('success', f"{'70085.25':<15} | {'0.500':<12} | {'BID':<6}")
    stop_boxed_mode()

def ticker_movie():
    start_boxed_mode("TICKER")
    display_message('action_start', "Fetching ticker for BTC-USDT")
    time.sleep(get_sleep_time(0.8))
    display_message('action_stop', "Retrieved ticker for BTC-USDT", result_icon="✓")
    display_message('info', "  Symbol: BTC/USDT")
    display_message('info', "  Last:   70100.00")
    display_message('info', "  Bid:    70095.50")
    display_message('info', "  Ask:    70105.25")
    display_message('info', "  24h %:  +2.45%")
    stop_boxed_mode()

def ohlcv_movie():
    start_boxed_mode("OHLCV CANDLES")
    display_message('action_start', "Fetching 1h candles for BTC-USDT")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Retrieved 10 candles", result_icon="✓")
    display_message('info', f"{'Timestamp':<20} | {'Open':<10} | {'High':<10} | {'Low':<10} | {'Close':<10}")
    display_message('info', "-" * 70)
    display_message('success', f"{'2026-02-19 10:00':<20} | {'69500.00':<10} | {'70200.00':<10} | {'69400.00':<10} | {'70100.00':<10}")
    display_message('success', f"{'2026-02-19 09:00':<20} | {'68800.00':<10} | {'69600.00':<10} | {'68750.00':<10} | {'69500.00':<10}")
    stop_boxed_mode()

def funding_movie():
    start_boxed_mode("FUNDING RATE")
    display_message('action_start', "Fetching current funding rate for BTC-USDT")
    time.sleep(get_sleep_time(0.8))
    display_message('action_stop', "Current Funding Rate: 0.0001", result_icon="✓")
    stop_boxed_mode()

def funding_history_movie():
    start_boxed_mode("FUNDING HISTORY")
    display_message('action_start', "Fetching historical funding payments")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Retrieved recent payments", result_icon="✓")
    display_message('info', f"{'Date':<20} | {'Pair':<10} | {'Rate':<10} | {'Payment':<10}")
    display_message('info', "-" * 55)
    display_message('success', f"{'2026-02-19 12:00':<20} | {'BTC/USDT':<10} | {'0.0001':<10} | {'-1.25':<10}")
    display_message('success', f"{'2026-02-19 04:00':<20} | {'BTC/USDT':<10} | {'0.0001':<10} | {'-1.25':<10}")
    stop_boxed_mode()

STEPS = {
    "markets": {
        "objective": "Instant Market Insights",
        "command_args": ["markets"],
        "explanation": "Discover opportunities instantly. List tradable pairs and query critical data like funding rates. Stay ahead of the market without leaving your terminal.",
        "display_cmd": "bitmango markets --exchange binance",
        "movie": market_data_movie,
        "use_case": "How it helps make money: Funding rate arbitrage. Identify pairs with high positive funding to collect payments by holding short positions. \nPrevent losing money: Avoid 'longing' assets with extremely high positive funding where the 'carry cost' will eat your profits.",
        "pro_tip": "High funding rates are often a leading indicator of a crowded trade. Use 'markets' to find quieter, more profitable opportunities."
    },
    "order_book": {
        "objective": "Deep Market Analysis",
        "command_args": ["query_order_book", "--pair", "btc-usdt"],
        "explanation": "Visualize market liquidity. The 'query_order_book' command pulls real-time L2 data to show buy and sell walls.",
        "display_cmd": "bitmango query_order_book --pair btc-usdt --depth 5",
        "movie": order_book_movie,
        "use_case": "How it helps make money: Scalping. Identify large 'buy walls' and enter long just above them for high-probability, low-risk setups. \nPrevent losing money: Don't market buy into a 'thin' book where your order will cause massive slippage.",
        "pro_tip": "Look for 'Imbalances' in the book depth. If Bids are 10x larger than Asks, the path of least resistance is usually UP."
    },
    "ticker": {
        "objective": "Quick Price Check",
        "command_args": ["ticker", "--pair", "btc-usdt"],
        "explanation": "Get the most critical price data at a glance. 'ticker' provides the last price, current bid/ask spread, and 24h percentage change.",
        "display_cmd": "bitmango ticker --pair btc-usdt",
        "movie": ticker_movie,
        "use_case": "How it helps make money: Arbitrage. Quickly compare prices across multiple exchanges with 'ticker' to identify mispricings. \nPrevent losing money: Always check the 'bid/ask spread' before entering a large position to ensure you aren't paying too much in implicit slippage costs.",
        "pro_tip": "The 'bid/ask spread' is a direct measure of market liquidity. A widening spread often precedes a high-volatility event."
    },
    "ohlcv": {
        "objective": "Technical Context",
        "command_args": ["ohlcv", "--pair", "btc-usdt"],
        "explanation": "Analyze historical price action. The 'ohlcv' command pulls Open, High, Low, Close, and Volume data for any supported timeframe.",
        "display_cmd": "bitmango ohlcv --pair btc-usdt --timeframe 1h --limit 10",
        "movie": ohlcv_movie,
        "use_case": "How it helps make money: Trend identification. Use OHLCV data to confirm if a market is in an uptrend, downtrend, or range-bound before deploying capital. \nPrevent losing money: Avoid 'buying the top' by using OHLCV data to see if price is currently at a historical resistance level.",
        "pro_tip": "Volume often precedes price. Use 'ohlcv' to look for volume spikes that confirm the strength of a price breakout."
    },
    "funding": {
        "objective": "Live Yield Analysis",
        "command_args": ["funding", "--pair", "btc-usdt"],
        "explanation": "Identify the 'carry cost' or 'yield' of your futures positions instantly. The 'funding' command returns the current real-time funding rate for any pair.",
        "display_cmd": "bitmango funding --pair btc-usdt",
        "movie": funding_movie,
        "use_case": "How it helps make money: Carry Trade. Identify assets where you get paid to hold a position (e.g. going short when funding is positive). \nPrevent losing money: Extremely high funding can turn a profitable trade into a loss over time. Monitor it closely.",
        "pro_tip": "Funding rates are settled every 8 hours on most exchanges. Check 'funding' 1 hour before settlement to decide if you want to hold through it."
    },
    "funding_history": {
        "objective": "Historical Yield Audit",
        "command_args": ["funding-history", "--pair", "btc-usdt"],
        "explanation": "Audit your actual yield payments over time. 'funding-history' shows exactly how much you paid or received in funding for a specific pair.",
        "display_cmd": "bitmango funding-history --pair btc-usdt",
        "movie": funding_history_movie,
        "use_case": "Prevent losing money: Cumulative funding costs can be significant. Audit your history to ensure funding isn't eroding your capital faster than your strategy is growing it.",
        "pro_tip": "Analyze funding history across different exchanges. Some exchanges consistently have lower funding for the same pair, offering a structural advantage for long-term positions."
    }
}
