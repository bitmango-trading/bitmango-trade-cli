import time
from bitmango_free.output import display_message, start_boxed_mode, stop_boxed_mode
from bitmango_free.demo_helper import get_sleep_time

def setup_movie():
    start_boxed_mode("INITIAL SETUP")
    display_message('info', "Initializing BitMango Environment...")
    time.sleep(get_sleep_time(0.5))
    display_message('success', "Clone: git clone bitmango-trade-cli-dev ✓")
    time.sleep(get_sleep_time(0.5))
    display_message('info', "Initializing Secure Vault...")
    display_message('success', "Vault Setup: ./bitmango-vault --setup ✓")
    time.sleep(get_sleep_time(0.5))
    display_message('success', "Environment Ready for Deployment! 🚀")
    stop_boxed_mode()

STEPS = {
    "human": {
        "objective": "Standard Onboarding (Human)",
        "command_args": ["ticker", "--pair", "btc-usdt"], 
        "explanation": "The human onboarding path focuses on manual verification and exploration of the CLI's unified interface.",
        "display_cmd": "git clone <url> && ./bitmango-vault --setup && ./bitmango-help all",
        "movie": setup_movie,
        "use_case": "Perfect for active traders who want to manually control their entries, exits, and risk management with 100% precision.",
        "pro_tip": "Run './bitmango-help all' to experience the full walkthrough of professional execution commands."
    },
    "ai-bot": {
        "objective": "Automated Onboarding (AI/Agent)",
        "command_args": ["ticker", "--pair", "btc-usdt"], 
        "explanation": "BitMango is designed to be fully 'Agentic-Ready'. AI agents can use the same CLI tools to build and manage complex trading bots.",
        "display_cmd": 'Tell AI: "Build a bot using bitmango on the simulated exchange"',
        "movie": setup_movie,
        "use_case": "Ideal for developers building autonomous trading agents that require a reliable, multi-exchange execution engine.",
        "pro_tip": "Provide the AI with the './bitmango-help all' output to give it a complete mental model of available commands."
    }
}
