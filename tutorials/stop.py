import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def trailing_stop_movie():
    start_boxed_mode("TRAILING STOP")
    display_message('info', "Starting Pro Trailing Stop for BTC-USDT")
    display_message('info', "Initial Price: 69800.00, Initial Trigger: 69102.00")
    time.sleep(get_sleep_time(1))
    
    display_message('action_start', "Monitoring BTC-USDT Price: 69800.00 | Stop: 69102.00")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Monitoring BTC-USDT Price: 69800.00 | Stop: 69102.00", result_icon="⏳")
    
    display_message('action_start', "Trailing Update: New Peak 72000.00, New Trigger 71280.00")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Trailing Update: New Peak 72000.00, New Trigger 71280.00", result_icon="📈")
    
    display_message('action_start', "Trailing Update: New Peak 75000.00, New Trigger 74250.00")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Trailing Update: New Peak 75000.00, New Trigger 74250.00", result_icon="📈")
    
    display_message('warning', "TRAILING STOP TRIGGERED: Price 74000.00 <= 74250.00 💥")
    time.sleep(get_sleep_time(1))
    
    display_message('info', "Executing Market Exit")
    display_message('success', "Trailing Stop Complete 🏁")
    stop_boxed_mode()

def native_stop_movie():
    start_boxed_mode("NATIVE STOP")
    display_message('action_start', "Placing STOP_MARKET sell order for 0.1 BTC at $65,000.00")
    time.sleep(get_sleep_time(1.2))
    display_message('action_stop', "Placing STOP_MARKET sell order for 0.1 BTC at $65,000.00", result_icon="✓")
    display_message('success', "Native stop order confirmed on Binance matching engine", icon="🛡️")
    stop_boxed_mode()

def ghost_stop_movie():
    start_boxed_mode("GHOST STOP")
    display_message('info', "Initializing Ghost Stop (Hidden)")
    display_message('info', "Trigger Price: 65,000.00 (Order not sent to exchange)")
    time.sleep(get_sleep_time(1))
    
    display_message('action_start', "Monitoring Price: 66,200.00")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Monitoring Price: 66,200.00", result_icon="⏳")
    
    display_message('action_start', "Monitoring Price: 64,950.00")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Price 64,950.00 hit trigger 65,000.00", result_icon="💥")
    
    display_message('warning', "TRIGGERED: Price 64,950.00 <= 65,000.00")
    
    display_message('action_start', "Executing Immediate Market Sell")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Executing Immediate Market Sell", result_icon="✓")
    display_message('success', "Position closed successfully")
    stop_boxed_mode()

STEPS = {
    "stop": {
        "objective": "Intelligent Profit Protection",
        "command_args": ["stop", "--stop-type", "trailing", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--callback-percentage", "0.01"],
        "explanation": "Advanced algorithmic intelligence. The 'stop' command with '--stop-type trailing' monitors price peaks and trails your stop-loss automatically. Lock in gains while letting winners run.",
        "display_cmd": "bitmango stop --stop-type trailing --pair btc-usdt --callback-percentage 0.01 --size 0.1",
        "movie": trailing_stop_movie,
        "use_case": "How it helps make money: Trailing stops automatically 'lock in' unrealized profits as the price moves in your favor, ensuring you exit near the top. \nPrevent losing money: It prevents a winning trade from turning into a losing trade by constantly raising the floor.",
        "pro_tip": "Run Trailing Stops in a background screen or tmux session to ensure they keep polling even if your local terminal closes."
    },
    "native-stop": {
        "objective": "Low-Latency Native Stops",
        "command_args": ["stop", "--stop-type", "native", "--pair", "btc-usdt", "--direction", "buy", "--size", "0.1", "--stop-price", "65000"],
        "explanation": "Maximum reliability for volatile moves. Native stops work independently of your terminal. They live on the exchange matching engine for 24/7 protection.",
        "display_cmd": "bitmango stop --pair btc-usdt --stop-price 65000 --size 0.1",
        "movie": native_stop_movie,
        "use_case": "Prevent losing money: Native stops are the most robust form of insurance. They trigger even if your internet goes down or the CLI is closed, preventing catastrophic losses.",
        "pro_tip": "Always have a native stop-loss in place, even if you are using an advanced CLI-side strategy, as a 'hard floor' safety net."
    },
    "ghost-stop": {
        "objective": "Hidden Execution (Ghost Stop)",
        "command_args": ["stop", "--stop-type", "ghost", "--pair", "btc-usdt", "--stop-price", "65000"],
        "explanation": "Stealth mode. Ghost stops reside only in your CLI memory and are not visible on the order book. They trigger a market order only when the price is hit.",
        "display_cmd": "bitmango stop --stop-type ghost --pair btc-usdt --stop-price 65000",
        "movie": ghost_stop_movie,
        "use_case": "How it helps make money: By hiding your stop from the exchange, you prevent 'Stop Hunting' where market makers push price briefly to hit visible stops. \nPrevent losing money: Preserves your entry strategy by not signaling your exit points to other participants.",
        "pro_tip": "Ghost stops are perfect for 'Liquidity Grabs' where price briefly spikes to a level just to trigger stop-losses before reversing."
    }
}
