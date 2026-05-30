import sys
import importlib
from bitmango.output import display_message
from bitmango.messages import get_message

class ExchangeError(Exception):
    def __init__(self, original_exception):
        self.original_exception = original_exception
        super().__init__(str(original_exception))

class UnsupportedError(Exception):
    def __init__(self, message):
        super().__init__(message)

def handle_unsupported_error(exchange_name, e):
    """
    Handles cases where a feature is explicitly not supported or implemented.
    Raises UnsupportedError to signal UNSUPPORTED to the verification suite.
    """
    msg = get_message("errors.unsupported_feature", exchange=exchange_name, error=e)
    display_message('warning', msg)
    raise UnsupportedError(msg)

def handle_exchange_error(exchange_name, e, args):
    """
    Handles exchange-specific errors by providing more detailed feedback.
    """
    display_message('error', get_message("errors.exchange_specific", error=e))

    try:
        # Dynamically import the exchange-specific error handler
        error_handler_module = importlib.import_module(f"bitmango.exchange.{exchange_name}.{exchange_name}_errors")
        error_handler_func = getattr(error_handler_module, "handle_error")
        error_handler_func(e, args)
    except (ImportError, AttributeError):
        # Fallback to generic error message if no specific handler is found
        display_message('error', get_message("errors.no_handler", exchange=exchange_name))

    raise e
