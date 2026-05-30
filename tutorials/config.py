import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def config_movie():
    start_boxed_mode("CONFIGURATION")
    display_message('info', "Loading BitMango Config Environment Variables")
    time.sleep(get_sleep_time(0.5))
    display_message('success', "BITMANGO_MAX_ORDER_USD: $100.00 (Default)")
    display_message('success', "BITMANGO_MAX_STALE_SECONDS: 10 (Default)")
    display_message('success', "BITMANGO_MAX_PRICE_DEVIATION: 5% (Default)")
    time.sleep(get_sleep_time(1))
    display_message('warning', "PROFESSIONAL CONFIGURATION: Order Safety Cap is set to $1,000,000.00. ⚠️")
    display_message('info', "Suppressing Warnings with BITMANGO_SAFETY_OVERRIDE=true...")
    time.sleep(get_sleep_time(0.5))
    display_message('success', "Safety Warnings: SILENCED", icon="🔕")
    stop_boxed_mode()

STEPS = {
    "config": {
        "objective": "BitMango Configuration & Environment",
        "command_args": ["ticker", "--pair", "btc-usdt"], # dummy command
        "explanation": "BitMango is configured via **environment variables** or a **.env** file. This approach is standard for high-performance trading bots and automation scripts.",
        "display_cmd": "cat config.env.example",
        "movie": config_movie,
        "use_case": "How it helps make money: Configurable risk caps allow you to scale your capital as your confidence grows. \nPrevent losing money: Starting with a $100 cap ensures you don't accidentally risk more than intended before your environment is fully tested.",
        "pro_tip": "Copy 'config.env.example' to '.env' in your project root to start with standard safe defaults. Use 'pro_config.env.example' for high-throughput institutional trading."
    },
    "safety-override": {
        "objective": "Suppressing Configuration Warnings",
        "command_args": ["ticker", "--pair", "btc-usdt"], # dummy command
        "explanation": "Professional traders using relaxed safety caps may find the startup warnings noisy. You can silence them using a safety override.",
        "display_cmd": "export BITMANGO_SAFETY_OVERRIDE=true",
        "movie": config_movie,
        "use_case": "How it helps make money: Silencing warnings ensures that automated bot logs are clean and only contain relevant execution data. \nPrevent losing money: Only use the override once you have fully verified your production environment configuration.",
        "pro_tip": "Never use BITMANGO_SAFETY_OVERRIDE during your initial development or testing phase."
    }
}
