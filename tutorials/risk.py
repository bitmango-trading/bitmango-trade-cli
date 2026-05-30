import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def risk_movie():
    start_boxed_mode("LEVERAGE")
    display_message('action_start', "Setting leverage to 20x for BTC-USDT")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Leverage set to 20x for BTC-USDT", result_icon="✓")
    stop_boxed_mode()
    time.sleep(get_sleep_time(1))
    start_boxed_mode("MARGIN")
    display_message('action_start', "Setting margin mode to ISOLATED for BTC-USDT")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Margin mode set to ISOLATED for BTC-USDT", result_icon="✓")
    stop_boxed_mode()

def kill_switch_movie():
    start_boxed_mode("KILL SWITCH")
    display_message('action_start', "Configuring Universal Kill Switch")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "Max loss threshold set to $500.00", result_icon="✓")
    display_message('info', "Safety Monitor: ACTIVE (Polling interval: 1s)")
    time.sleep(get_sleep_time(1))
    display_message('warning', "THRESHOLD HIT: Net Loss reached -$500.00")
    display_message('action_start', "EMERGENCY: Closing 3 open positions")
    time.sleep(get_sleep_time(0.5))
    display_message('action_stop', "All positions closed successfully", result_icon="🛡️")
    display_message('success', "Capital Protected: $12,450.00 saved from further ruin", icon="🔒")
    stop_boxed_mode()

def position_mode_movie():
    start_boxed_mode("POSITION MODE")
    display_message('action_start', "Setting position mode to Hedge")
    time.sleep(get_sleep_time(1))
    display_message('action_stop', "Position mode set to HEDGE (Multi-Directional)", result_icon="✓")
    display_message('info', "You can now hold both LONG and SHORT positions simultaneously.")
    stop_boxed_mode()

def safety_cap_movie():
    start_boxed_mode("SAFETY CAP")
    display_message('info', "Current Order Cap: $100.00 (Tight Default)")
    display_message('action_start', "Placing order for $5,000.00")
    time.sleep(get_sleep_time(1))
    display_message('error', "RISK BREACH: Order value $5,000.00 exceeds safety cap of $100.00")
    display_message('info', "To increase: export BITMANGO_MAX_ORDER_USD=10000")
    stop_boxed_mode()

STEPS = {
    "safety-cap": {
        "objective": "Capital Protection Defaults",
        "command_args": ["ticker", "--pair", "btc-usdt"], # dummy command
        "explanation": "BitMango enforces a tight **$100 default order cap**. This is a 'Security by Default' mandate to prevent accidental large exposures.",
        "display_cmd": "export BITMANGO_MAX_ORDER_USD=10000",
        "movie": safety_cap_movie,
        "use_case": "Prevent losing money: Protects you from fat-finger errors or untested bot behavior. You must explicitly authorize larger trades by setting an environment variable.",
        "pro_tip": "Set BITMANGO_MAX_ORDER_USD in your .bashrc or .env file to make it permanent for your session."
    },
    "leverage": {
        "objective": "Dynamic Risk Configuration",
        "command_args": ["leverage", "--pair", "btc-usdt", "--leverage", "20"],
        "explanation": "Adjust your risk profile on the fly. BitMango makes setting leverage and margin modes consistent across different exchange architectures. Safely scale your capital usage.",
        "display_cmd": "bitmango leverage --pair btc-usdt --leverage 20 --exchange binance",
        "movie": risk_movie,
        "use_case": "How it helps make money: Increasing leverage allows you to capture larger profits with smaller capital when your conviction is high. \nPrevent losing money: Lowering leverage immediately reduces your liquidation price and overall portfolio exposure.",
        "pro_tip": "Remember: High leverage doesn't mean high risk if your position size is small. Use leverage to free up capital, not just to gamble."
    },
    "margin": {
        "objective": "Dynamic Risk Configuration",
        "command_args": ["margin", "--pair", "btc-usdt", "--mode", "isolated"],
        "explanation": "Adjust your risk profile on the fly. BitMango makes setting leverage and margin modes consistent across different exchange architectures. Safely scale your capital usage.",
        "display_cmd": "bitmango margin --pair btc-usdt --mode isolated --exchange binance",
        "movie": risk_movie,
        "use_case": "Prevent losing money: 'Isolated' margin restricts losses to only the specific trade, protecting the rest of your account balance from a single bad position.",
        "pro_tip": "Use 'Isolated' mode when testing new, aggressive strategies. Use 'Cross' mode for your core, well-tested portfolio."
    },
    "kill-switch": {
        "objective": "Global Safety Net",
        "command_args": ["kill-switch", "--max-loss", "500"],
        "explanation": "Your ultimate capital protection. The Kill Switch runs a background monitor on your total equity. It will liquidate all positions if your risk threshold is hit.",
        "display_cmd": "bitmango kill-switch --max-loss 500",
        "movie": kill_switch_movie,
        "use_case": "Prevent losing money: The Kill Switch is the ultimate 'circuit breaker'. It prevents total account wipeout (ruin) by exiting everything once a maximum daily loss is reached.",
        "pro_tip": "Set your Kill Switch at the start of every trading week. It's your 'Emotional Circuit Breaker' for when things get chaotic."
    },
    "position-mode": {
        "objective": "Position Strategy",
        "command_args": ["position-mode", "--pair", "btc-usdt", "--mode", "hedge"],
        "explanation": "Switch between Hedge Mode (simultaneous long/short) and One-Way Mode. Crucial for advanced hedging strategies.",
        "display_cmd": "bitmango position-mode --pair btc-usdt --mode hedge",
        "movie": position_mode_movie,
        "use_case": "How it helps make money: Hedge mode allows you to stay in a long-term uptrend while simultaneously capturing short-term downward corrections. \nPrevent losing money: Allows for 'neutral' delta strategies where you hedge your spot holdings with futures shorts.",
        "pro_tip": "Not all exchanges support Hedge mode. BitMango will warn you if you try to set it on an exchange that only supports One-Way."
    }
}
