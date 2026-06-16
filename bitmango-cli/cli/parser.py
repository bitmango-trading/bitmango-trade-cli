import argparse
import sys
import os
import re
import pyotp
from bitmango.output import display_message, prompt_user, output as output_manager, Verbosity
from bitmango.vault import load_vault, is_session_valid, create_session
from bitmango.messages import get_message

def confirm_order(prompt=None, no_confirm=False):
    """Prompt user for confirmation before proceeding."""
    if no_confirm:
        return True
    if prompt is None:
        prompt = get_message("cli.confirm_order")
    user_input = input(prompt).lower()
    return user_input == "y"

def security_excepthook(type, value, tb):
    """Global exception handler that sanitizes tracebacks."""
    import traceback
    # Redact common secret keywords
    secret_patterns = [
        r"(apiKey['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])",
        r"(secret['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])",
        r"(password['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])",
        r"(token['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])",
    ]
    tb_text = "".join(traceback.format_exception(type, value, tb))
    sanitized_text = tb_text
    for pattern in secret_patterns:
        sanitized_text = re.sub(pattern, r"\1********\3", sanitized_text, flags=re.IGNORECASE)
    
    from bitmango.output import display_message
    display_message('error', get_message("cli.fatal_crash"))
    for line in sanitized_text.splitlines():
        display_message('error', line)
    # Note: we don't sys.exit here, we let the normal flow handle it or re-raise
    raise value

def disable_core_dumps():
    """Attempts to disable core dumps."""
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except Exception: pass

def verify_admin_session():
    """Ensures the user has an active TOTP session."""
    if is_session_valid(): return True
    vault = load_vault()
    if not vault: return True
    ttl = vault.get("config", {}).get("session_ttl", 10)
    if ttl == 0: return True
    secret = vault.get("config", {}).get("totp_secret")
    if not secret: return True
    display_message('warning', get_message("cli.admin_session_required"))
    display_message('info', get_message("cli.high_risk_auth"))
    totp = pyotp.TOTP(secret)
    for i in range(3):
        code = prompt_user(get_message("cli.totp_prompt", attempt=i+1)).strip()
        if totp.verify(code):
            display_message('success', get_message("cli.session_authorized"))
            create_session(ttl)
            return True
        display_message('error', get_message("cli.invalid_code"))
    display_message('error', get_message("cli.too_many_attempts"))
    raise PermissionError(get_message("cli.admin_auth_failed"))

def get_parser(core_commands):
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--sandbox', action='store_true')
    parent_parser.add_argument('-v', '--verbose', action='store_true')
    parent_parser.add_argument('--debug', action='store_true')
    parent_parser.add_argument('--market-type', choices=['spot', 'futures'], default='futures')
    parent_parser.add_argument('--exchange')
    parent_parser.add_argument('--no-confirm', action='store_true')
    parent_parser.add_argument('--no-color', action='store_true')
    parent_parser.add_argument('-o', '--output', choices=['human', 'json'], default='human')
    parent_parser.add_argument('--wait', action='store_true', help=get_message("cli.wait_help"))

    parser = argparse.ArgumentParser(description="Bitmango.win - Trade CLI Tool")
    parser.add_argument('--daemonize', action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    # Entry
    entry_parser = subparsers.add_parser('entry', parents=[parent_parser])
    entry_parser.add_argument('--direction', choices=['buy', 'long', 'sell', 'short'], required=True)
    entry_group = entry_parser.add_mutually_exclusive_group(required=True)
    entry_group.add_argument('--size', type=float)
    entry_group.add_argument('--percent', type=int)
    entry_parser.add_argument('--price', type=float)
    entry_parser.add_argument('--order-type', choices=['market', 'limit'], default='limit')
    entry_parser.add_argument('--pair')
    entry_parser.add_argument('--smart-order', action='store_true')
    entry_parser.add_argument('--price-range-min', type=float)
    entry_parser.add_argument('--price-range-max', type=float)
    entry_parser.add_argument('--chunk-size', type=float)

    # Buy/Sell Aliases
    for cmd in ['buy', 'sell']:
        p = subparsers.add_parser(cmd, parents=[parent_parser])
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument('--size', type=float)
        g.add_argument('--percent', type=int)
        p.add_argument('--price', type=float)
        p.add_argument('--order-type', choices=['market', 'limit'], default='limit')
        p.add_argument('--pair')
        p.add_argument('--smart-order', action='store_true')
    
    # Cancel
    cancel_parser = subparsers.add_parser('cancel', parents=[parent_parser])
    cancel_subparsers = cancel_parser.add_subparsers(dest='cancel_command')
    all_c = cancel_subparsers.add_parser('all', parents=[parent_parser])
    all_c.add_argument('--pair', required=True)
    spec_c = cancel_subparsers.add_parser('specific', parents=[parent_parser])
    spec_c.add_argument('--direction', choices=['buy', 'long', 'sell', 'short'], required=True)
    spec_c.add_argument('--size', type=float, required=True)
    spec_c.add_argument('--pair')
    
    # Stop
    stop_parser = subparsers.add_parser('stop', parents=[parent_parser])
    stop_parser.add_argument('--direction', choices=['buy', 'long', 'sell', 'short'])
    stop_parser.add_argument('--size', type=float, required=True)
    stop_parser.add_argument('--stop-price', type=float)
    stop_parser.add_argument('--current-price', type=float)
    stop_parser.add_argument('--stop-loss-percentage', type=float)
    stop_parser.add_argument('--take-profit-percentage', type=float)
    stop_parser.add_argument('--order-type', choices=['market', 'limit', 'stop_loss', 'take_profit'], default='limit')
    stop_parser.add_argument('--stop-type', choices=['native', 'ghost', 'trailing'], default='native')
    stop_parser.add_argument('--callback-percentage', type=float)
    stop_parser.add_argument('--pair')
    stop_parser.add_argument('--smart-stop', action='store_true')
    stop_parser.add_argument('--price-range-min', type=float)
    stop_parser.add_argument('--price-range-max', type=float)
    stop_parser.add_argument('--chunk-size', type=float)
    stop_parser.add_argument('--poll-interval', type=float, default=5.0, help=get_message("cli.stop_poll_help"))

    # Exit / Close
    exit_parser = subparsers.add_parser('exit', parents=[parent_parser])
    exit_subs = exit_parser.add_subparsers(dest='exit_command')
    exit_all = exit_subs.add_parser('all', parents=[parent_parser])
    exit_spec = exit_subs.add_parser('specific', parents=[parent_parser])
    exit_spec.add_argument('--position')
    exit_spec.add_argument('--size', type=float, required=True)
    exit_spec.add_argument('--price', type=float)
    exit_spec.add_argument('--order-type', choices=['market', 'limit'], default='limit')
    exit_spec.add_argument('--pair')
    exit_spec.add_argument('--smart-order', action='store_true')
    exit_spec.add_argument('--price-range-min', type=float)
    exit_spec.add_argument('--price-range-max', type=float)
    exit_spec.add_argument('--chunk-size', type=float)

    close_p = subparsers.add_parser('close', parents=[parent_parser])
    close_p.add_argument('--pair', required=True)
    close_p.add_argument('--size', type=float)
    close_p.add_argument('--order-type', choices=['market', 'limit'], default='market')
    close_p.add_argument('--price', type=float)
    
    subparsers.add_parser('close-all', parents=[parent_parser])

    # Account & Market Data
    account_p = subparsers.add_parser('account', parents=[parent_parser])
    account_p.add_argument('--positions', action='store_true')
    account_p.add_argument('--balance', action='store_true')
    subparsers.add_parser('markets', parents=[parent_parser])
    ticker_p = subparsers.add_parser('ticker', parents=[parent_parser])
    ticker_p.add_argument('--pair', required=True)
    ticker_p.add_argument('--stream', action='store_true', help=get_message("cli.ticker_stream_help"))
    history_p = subparsers.add_parser('history', parents=[parent_parser])
    history_p.add_argument('--pair')
    
    # Settings & Misc
    lev_p = subparsers.add_parser('leverage', parents=[parent_parser])
    lev_p.add_argument('--pair', required=True)
    lev_p.add_argument('--leverage', type=int, required=True)
    
    marg_p = subparsers.add_parser('margin', parents=[parent_parser])
    marg_p.add_argument('--pair', required=True)
    marg_p.add_argument('--mode', choices=['cross', 'isolated'], required=True)
    
    trans_p = subparsers.add_parser('transfer', parents=[parent_parser])
    trans_p.add_argument('--currency', required=True)
    trans_p.add_argument('--amount', type=float, required=True)
    trans_p.add_argument('--from-account', choices=['spot', 'futures'], required=True)
    trans_p.add_argument('--to-account', choices=['spot', 'futures'], required=True)
    
    funding_p = subparsers.add_parser('funding', parents=[parent_parser])
    funding_p.add_argument('--pair', required=True)
    subparsers.add_parser('funding-history', parents=[parent_parser]).add_argument('--pair')
    
    pm_p = subparsers.add_parser('position-mode', parents=[parent_parser])
    pm_p.add_argument('--pair', required=True)
    pm_p.add_argument('--mode', choices=['oneway', 'hedge'], required=True)
    
    subparsers.add_parser('ledger', parents=[parent_parser]).add_argument('--currency', default='USDT')
    subparsers.add_parser('deposits', parents=[parent_parser]).add_argument('--currency')
    subparsers.add_parser('withdrawals', parents=[parent_parser]).add_argument('--currency')
    subparsers.add_parser('position-risk', parents=[parent_parser]).add_argument('--pair')
    
    # OHLCV
    ohlcv_parser = subparsers.add_parser('ohlcv', parents=[parent_parser])
    ohlcv_parser.add_argument('--pair', required=True)
    ohlcv_parser.add_argument('--timeframe', default='1h')
    ohlcv_parser.add_argument('--limit', type=int, default=10)
    ohlcv_parser.add_argument('--stream', action='store_true', help=get_message("cli.ohlcv_stream_help"))
    ohlcv_parser.add_argument('--rsi', type=int, help=get_message("cli.rsi_help"))
    ohlcv_parser.add_argument('--ema', type=int, help=get_message("cli.ema_help"))

    # Open Orders
    subparsers.add_parser('open_orders', parents=[parent_parser]).add_argument('--pair')

    # Trades
    subparsers.add_parser('trades', parents=[parent_parser]).add_argument('--pair')

    # Order Status
    os_parser = subparsers.add_parser('order-status', parents=[parent_parser])
    os_parser.add_argument('--order-id', required=True)
    os_parser.add_argument('--pair')

    # Closed Orders
    co_parser = subparsers.add_parser('closed-orders', parents=[parent_parser])
    co_parser.add_argument('--pair', required=True)
    co_parser.add_argument('--limit', type=int, default=20)

    qob_parser = subparsers.add_parser('query_order_book', parents=[parent_parser])
    qob_parser.add_argument('--pair', required=True)
    qob_parser.add_argument('--stream', action='store_true', help=get_message("cli.qob_stream_help"))

    return parser, subparsers, parent_parser
