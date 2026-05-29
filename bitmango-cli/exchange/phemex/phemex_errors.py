import importlib
import json
import re
from bitmango.output import display_message
from bitmango.messages import get_message

def display_balance(exchange_name, args):
    display_message('debug', f"exchange_name in display_balance: '{exchange_name}'")
    try:
        module_path = f"bitmango.exchange.{exchange_name}.account_open_positions"
        module = importlib.import_module(module_path)
        ExchangeClass = getattr(module, f"{exchange_name.capitalize()}AccountPositions")
        exchange_instance = ExchangeClass(args)
        exchange_instance.balance(args)
    except Exception as e:
        display_message('error', get_message("exchange.fetch_error", item="balance", exchange=exchange_name, error=e))

def handle_error(e, args):
    """
    Handles Phemex specific errors.
    """
    error_code = None
    error_string = str(e)

    # Try to parse the error string as JSON
    try:
        match = re.search(r'phemex (.*)', error_string)
        if match:
            json_part = match.group(1)
            error_data = json.loads(json_part)
            if 'code' in error_data:
                error_code = error_data['code']
    except json.JSONDecodeError:
        pass

    if error_code is None:
        if hasattr(e, 'json') and e.json and 'code' in e.json:
            error_code = e.json['code']
        elif hasattr(e, 'code'):
            error_code = e.code

    display_message('debug', f"error_code={error_code}, type={type(error_code)}")

    if error_code == 11001 or error_code == 11106: # 11001 is another insufficient balance code
        display_message('warning', get_message("exchange.phemex_insufficient_funds"))
        display_balance(args.exchange, args)
    elif error_code == 39100:
        display_message('warning', get_message("exchange.phemex_order_too_small"))
        display_balance(args.exchange, args)
    elif error_code == 39999:
        display_message('warning', get_message("exchange.phemex_generic_error"))
        display_balance(args.exchange, args)
    else:
        display_message('error', get_message("exchange.phemex_error_code", code=error_code))
