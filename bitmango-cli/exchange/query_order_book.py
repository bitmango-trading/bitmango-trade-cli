from bitmango.output import display_message
from bitmango.exchange.functions import get_exchange_class

def query_order_book(exchange_name, args):
    """Queries the order book for a specific symbol."""
    ExchangeClass = get_exchange_class(exchange_name, command='query_order_book')
    if not ExchangeClass:
        display_message('error', f"No implementation found for exchange {exchange_name}")
        raise ValueError(f"No implementation found for exchange {exchange_name}")

    instance = ExchangeClass(args)
    try:
        return instance.query_order_book(args)
    except Exception as e:
        display_message('error', f"Query Error: {e}")
        raise e
