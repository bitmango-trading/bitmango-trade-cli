import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def entry_movie():
    start_boxed_mode("ENTRY")
    display_message('action_start', "Placing native market order for 0.1 BTC on Binance")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Placing native market order for 0.1 BTC on Binance", result_icon="✓")
    display_message('success', "Order executed successfully: ord-99827341")
    stop_boxed_mode()

def limit_entry_movie():
    start_boxed_mode("ENTRY")
    display_message('action_start', "Placing Limit Buy order for 0.5 BTC at $68,500.00")
    time.sleep(get_sleep_time(0.8))
    display_message('action_stop', "Placing Limit Buy order for 0.5 BTC at $68,500.00", result_icon="✓")
    display_message('success', "Limit order confirmed in book: ord-99827342")
    stop_boxed_mode()

def smart_order_movie():
    start_boxed_mode("SMART ORDER")
    display_message('info', "Initializing TWAP Smart Order for 10.0 BTC")
    display_message('info', "Price Range: 69,000 - 70,000 | Chunk Size: 0.5 BTC")
    time.sleep(get_sleep_time(1))
    
    display_message('action_start', "Executing Chunk 1/20: Buy 0.5 BTC @ Market")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Chunk 1 Filled @ 69,450.00", result_icon="✓")
    
    display_message('action_start', "Waiting for next interval (randomized)...")
    time.sleep(get_sleep_time(1))
    
    display_message('action_start', "Executing Chunk 2/20: Buy 0.5 BTC @ Market")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Chunk 2 Filled @ 69,480.00", result_icon="✓")
    
    display_message('info', "... continuing execution ...")
    display_message('success', "Execution complete. Average Fill: 69,465.00")
    display_message('success', "Slippage Savings: +$420.50 (vs Market Taker)", icon="💰")
    stop_boxed_mode()

STEPS = {
    "entry": {
        "objective": "Market Order Execution",
        "command_args": ["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--order-type", "market"],
        "explanation": "Standardize your trading across all exchanges. The 'entry' command provides a unified interface for immediate market execution. We are executing a 0.1 BTC spot market buy on Binance.",
        "display_cmd": "bitmango entry --exchange binance --pair btc-usdt --direction buy --size 0.1 --order-type market",
        "movie": entry_movie,
        "use_case": "Standardizing entry allows you to react instantly to market news across any exchange. \nPrevent losing money: Fast execution ensures you exit or enter at the price you intended before the market moves against you.",
        "pro_tip": "Save precious seconds during high volatility by using the 'buy' or 'sell' aliases directly. \nExample: bitmango buy --size 0.1 --pair BTC-USDT"
    },
    "limit": {
        "objective": "Limit Order Placement",
        "command_args": ["entry", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.5", "--order-type", "limit", "--price", "68500"],
        "explanation": "Gain precise price control. Use limit orders to wait for the market to come to you. This reduces slippage and improves entry quality.",
        "display_cmd": "bitmango entry --exchange binance --pair btc-usdt --direction buy --size 0.5 --order-type limit --price 68500",
        "movie": limit_entry_movie,
        "use_case": "How it helps make money: Entering at your specific price target maximizes your potential profit margin per trade. \nPrevent losing money: By avoiding market orders during high volatility, you prevent 'slippage' where you buy significantly higher than your intended price.",
        "pro_tip": "Always use Limit orders when your size is a significant percentage of the 1-minute volume to avoid paying 'the taker tax' (higher fees)."
    },
    "smart-order": {
        "objective": "Smart Execution (TWAP)",
        "command_args": ["entry", "--smart-order", "--pair", "btc-usdt", "--direction", "buy", "--size", "10", "--chunk-size", "0.5"],
        "explanation": "Minimize market impact for large positions. Smart Orders break down your trade into smaller chunks and execute them over time using a randomized TWAP algorithm.",
        "display_cmd": "bitmango entry --smart-order --pair btc-usdt --size 10 --chunk-size 0.5",
        "movie": smart_order_movie,
        "use_case": "How it helps make money: Large orders often 'move the needle' and cause price spikes. Smart orders hide your true size. \nPrevent losing money: TWAP prevents you from being 'hunted' by algorithmic bots that look for large market orders to trade against.",
        "pro_tip": "Combine --smart-order with --price-range-min/max to ensure you don't keep buying if the market suddenly rips away from your target zone."
    }
}
