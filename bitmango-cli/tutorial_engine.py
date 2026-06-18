import sys
import importlib
from bitmango.demo_helper import run_canned_step
from bitmango.output import display_message

# Nuitka Hint: Ensure tutorials package and its modules are bundled
if False:
    import tutorials.setup
    import tutorials.entry
    import tutorials.account
    import tutorials.stop
    import tutorials.risk
    import tutorials.config
    import tutorials.management
    import tutorials.market

def get_tutorial_steps(cmd):
    """Maps command to tutorial module and returns its STEPS."""
    mapping = {
        'setup': 'setup',
        'entry': 'entry', 'limit': 'entry', 'buy': 'entry', 'sell': 'entry', 'smart-order': 'entry',
        'account': 'account', 'positions': 'account', 'history': 'account', 'ledger': 'account', 'transfer': 'account', 'trades': 'account',
        'stop': 'stop', 'native-stop': 'stop', 'trailing-stop': 'stop', 'ghost-stop': 'stop',
        'leverage': 'risk', 'margin': 'risk', 'kill-switch': 'risk', 'position-mode': 'risk', 'risk': 'risk',
        'config': 'config',
        'open_orders': 'management', 'cancel': 'management', 'close': 'management', 'close-all': 'management', 'report': 'management',
        'markets': 'market', 'funding': 'market', 'query_order_book': 'market', 'ticker': 'market', 'ohlcv': 'market', 'funding-history': 'market'
    }
    
    module_name = mapping.get(cmd)
    if not module_name:
        return None
        
    try:
        # We try to import from tutorials package
        mod = importlib.import_module(f"tutorials.{module_name}")
        return getattr(mod, 'STEPS', {})
    except Exception as e:
        display_message('debug', f"Failed to load tutorial module {module_name}: {e}")
        return None

def run_help(requested_cmd):
    """Executes the help logic for a given command."""
    requested_cmd = requested_cmd.lower()
    
    # Special case for 'all'
    if requested_cmd == 'all':
        from demo.walkthrough import main as play_walkthrough
        play_walkthrough()
        return

    steps = get_tutorial_steps(requested_cmd)
    if not steps:
        display_message('error', f"No cinematic tutorial available for '{requested_cmd}'.")
        return
        
    # Sequences for comprehensive help
    HELP_SEQUENCES = {
        'setup': ['human', 'ai-bot'],
        'entry': ['entry', 'limit', 'smart-order'],
        'buy': ['entry', 'limit', 'smart-order'],
        'sell': ['entry', 'limit', 'smart-order'],
        'smart-order': ['smart-order'],
        
        'account': ['account', 'positions', 'history', 'ledger', 'trades', 'transfer'],
        'history': ['history', 'ledger', 'trades'],
        'ledger': ['ledger', 'history'],
        'trades': ['trades', 'history'],
        'transfer': ['transfer'],
        
        'stop': ['stop', 'native-stop', 'ghost-stop'],
        'native-stop': ['native-stop'],
        'trailing-stop': ['stop'],
        'ghost-stop': ['ghost-stop'],
        
        'leverage': ['leverage', 'margin'],
        'margin': ['leverage', 'margin'],
        'risk': ['safety-cap', 'leverage', 'margin', 'position-mode', 'kill-switch'],
        'position-mode': ['position-mode'],
        'kill-switch': ['kill-switch'],
        
        'config': ['config', 'safety-override'],
        
        'management': ['open_orders', 'cancel_all', 'close', 'close_all', 'report'],
        'open_orders': ['open_orders', 'cancel_all'],
        'cancel': ['open_orders', 'cancel_all'],
        'close': ['close', 'close_all'],
        'close-all': ['close_all'],
        'report': ['report'],
        
        'markets': ['markets', 'order_book', 'ticker', 'ohlcv', 'funding', 'funding_history'],
        'funding': ['funding', 'funding_history'],
        'funding-history': ['funding_history', 'funding'],
        'query_order_book': ['order_book'],
        'ticker': ['ticker'],
        'ohlcv': ['ohlcv']
    }
    
    keys_to_play = HELP_SEQUENCES.get(requested_cmd, [requested_cmd])
    
    # Filter only keys that exist in the loaded module's steps
    keys_to_play = [k for k in keys_to_play if k in steps]
    if not keys_to_play:
        # Fallback to the first available step in the module if specific key not found
        keys_to_play = [next(iter(steps.keys()))]

    for step_key in keys_to_play:
        s = steps[step_key]
        run_canned_step(
            s["objective"],
            s["command_args"],
            s["explanation"],
            s["movie"],
            display_cmd=s.get("display_cmd"),
            use_case=s.get("use_case"),
            pro_tip=s.get("pro_tip")
        )
