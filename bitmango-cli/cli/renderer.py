import datetime
import json
import sys
from bitmango.messages import get_message

def render_result(output_manager, result):
    """Final output rendering. Prints JSON or pretty-prints for humans."""
    if output_manager.json_mode:
        # Include accumulated messages in the final JSON object if it's a dict
        if isinstance(result, dict) and output_manager.messages:
            result['logs'] = output_manager.messages
        
        # Strip icons from all strings in the result dictionary for machine-purity
        def strip_recursive(obj):
            if isinstance(obj, str):
                return output_manager.strip_icons(obj)
            elif isinstance(obj, dict):
                return {k: strip_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [strip_recursive(i) for i in obj]
            return obj

        clean_result = strip_recursive(result)
        print(json.dumps(clean_result, indent=2))
        return

    # Human-Readable Formatting (Boxed UI)
    if not result or not isinstance(result, dict):
        return

    r_type = result.get('type')
    status = result.get('status', 'success')
    
    if status == 'error':
        output_manager.print_message('error', result.get('error', 'Unknown Error'))
        return

    if r_type == 'ticker':
        data = result.get('data', {})
        output_manager.print_message('info', get_message("market.ticker_symbol", symbol=result.get('symbol')))
        output_manager.print_message('info', get_message("market.ticker_last", last=data.get('last')))
        output_manager.print_message('info', get_message("market.ticker_bid", bid=data.get('bid')))
        output_manager.print_message('info', get_message("market.ticker_ask", ask=data.get('ask')))
        if data.get('percentage'):
            output_manager.print_message('info', get_message("market.ticker_change", change=data.get('percentage')))
    
    elif r_type == 'ohlcv':
        data = result.get('data', [])
        if not data:
            output_manager.print_message('warning', get_message("market.ohlcv_no_data"))
            return
        
        header = get_message("market.ohlcv_header", timestamp="Timestamp", close="Close", volume="Volume")
        has_rsi = any('rsi' in c.get('indicators', {}) for c in data)
        has_ema = any('ema' in c.get('indicators', {}) for c in data)
        
        if has_rsi: header += f" | {'RSI':<8}"
        if has_ema: header += f" | {'EMA':<10}"
        
        output_manager.print_message('info', header)
        output_manager.print_message('info', "-" * len(header))
        
        for rc in data[-10:]:
            dt = datetime.datetime.fromtimestamp(rc['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            line = get_message("market.ohlcv_entry", dt=dt, close=rc['close'], volume=rc['volume'])
            if has_rsi:
                rsi_val = rc.get('indicators', {}).get('rsi')
                line += f" | {rsi_val:<8.2f}" if rsi_val is not None else " | N/A"
            if has_ema:
                ema_val = rc.get('indicators', {}).get('ema')
                line += f" | {ema_val:<10.2f}" if ema_val is not None else " | N/A"
            output_manager.print_message('info', line)

    elif r_type == 'order':
        o = result.get('order', {})
        # Note: status.upper() and id are fine to keep as is for technical output
        output_manager.print_message('success', f"Order {o.get('status').upper()}: {o.get('id')}")
        output_manager.print_message('info', f"  {o.get('side').upper()} {o.get('type').upper()} {o.get('amount')} {o.get('symbol')}")
        if o.get('price'): output_manager.print_message('info', f"  Price: {o.get('price')}")
        output_manager.print_message('info', f"  Filled: {o.get('filled')} / Remaining: {o.get('remaining')}")

    elif r_type == 'balance':
        data = result.get('data', {})
        output_manager.print_message('info', f"Exchange: {result.get('exchange')} ({result.get('market_type')})")
        if 'total' in data:
            for currency, total in data['total'].items():
                if total > 0:
                    free = data['free'].get(currency, 0)
                    used = data['used'].get(currency, 0)
                    output_manager.print_message('info', get_message("account.balance_entry", currency=currency, total=total, free=free, used=used))

    elif r_type == 'positions':
        data = result.get('open_only', [])
        if not data:
            output_manager.print_message('warning', get_message("account.no_positions", exchange=result.get('exchange')))
        else:
            for pos in data:
                symbol = pos.get('symbol')
                side = pos.get('side', 'Unknown')
                size = pos.get('contracts', pos.get('amount', 0))
                entry = pos.get('entryPrice', 0)
                pnl = pos.get('unrealizedPnl', 0)
                leverage = pos.get('leverage', 1)
                output_manager.print_message('info', get_message("account.position_entry", symbol=symbol, side=side.upper(), size=size, entry=entry, pnl=pnl, leverage=leverage))

    elif r_type == 'ledger':
        entries = result.get('entries', [])
        if not entries:
            output_manager.print_message('warning', get_message("account.no_ledger", code=result.get('currency')))
        else:
            for entry in entries[:10]:
                output_manager.print_message('info', get_message("account.ledger_entry", dt=entry['datetime'], type=entry['type'], amount=entry['amount'], currency=entry['currency'], status=entry['status']))

    elif r_type == 'markets':
        symbols = result.get('symbols', [])
        for s in symbols[:20]:
            output_manager.print_message('info', f"  {s}")
        if len(symbols) > 20:
            output_manager.print_message('info', get_message("market.more_symbols", count=len(symbols)-20))

    else:
        output_manager.print_message('info', str(result))
