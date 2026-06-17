import time
from bitmango.output import display_message
from bitmango.exchange.functions import get_exchange_class
from bitmango.messages import get_message

def execute_order(exchange_name, args):
    """Executes a standard futures entry order."""
    ExchangeClass = get_exchange_class(exchange_name, command='entry')
    if not ExchangeClass:
        display_message('error', get_message("exchange.no_implementation", exchange=exchange_name))
        raise ValueError(f"No implementation found for exchange {exchange_name}")

    instance = ExchangeClass(args)
    symbol = instance._adapt_pair(args.pair)
    
    try:
        # Handle chunking for large orders
        if getattr(args, 'chunk_size', None):
            return _execute_chunked_order(instance, symbol, args)
        
        # Decide between entry and exit (for 'close' command mapping)
        is_exit = getattr(args, 'command', None) == 'exit'
        if is_exit:
            res = instance.exit(args)
        else:
            res = instance.entry(args)

        if res and res.get('status') == 'success':
            instance.verify_order_fulfillment(symbol, res, args.order_type)
        return res
    except Exception as e:
        display_message('error', get_message("cli.error_execution", error=e))
        raise e

def execute_exit_all(exchange_name, args):
    """Closes all positions on an exchange."""
    ExchangeClass = get_exchange_class(exchange_name, command='exit')
    if not ExchangeClass:
        display_message('error', get_message("exchange.no_implementation", exchange=exchange_name))
        raise ValueError(f"No implementation found for exchange {exchange_name}")

    instance = ExchangeClass(args)
    try:
        res = instance.close_all(args)
        instance.verify_position_closure(None) # Verify all
        return res
    except Exception as e:
        display_message('error', get_message("cli.error_stop_execution", error=e))
        raise e

def _execute_chunked_order(instance, symbol, args):
    """Splits a large order into smaller chunks."""
    total_size = float(args.size)
    chunk_size = float(args.chunk_size)
    
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
        
    num_chunks = int(total_size // chunk_size)
    remainder = total_size % chunk_size
    
    display_message('info', get_message("trade.chunked_order", chunks=num_chunks, size=chunk_size))
    
    results = []
    for i in range(num_chunks):
        args.size = chunk_size
        display_message('info', get_message("trade.placing_chunk", current=i+1, total=num_chunks))
        res = instance.entry(args)
        results.append(res)
        time.sleep(1) # Basic anti-spam
        
    if remainder > 0:
        args.size = remainder
        display_message('info', get_message("trade.placing_final"))
        res = instance.entry(args)
        results.append(res)
        
    return {"status": "success", "chunks": len(results)}
