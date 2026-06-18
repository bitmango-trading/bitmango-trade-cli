import ccxt
import os
import sys

def audit_bybit():
    print("Auditing Bybit CCXT capabilities...")
    exchange = ccxt.bybit()
    
    methods_to_check = [
        'fetchBalance', 'fetchPositions', 'fetchOrders', 'fetchOpenOrders',
        'fetchClosedOrders', 'fetchMyTrades', 'fetchLedger', 'fetchTicker',
        'fetchOrderBook', 'fetchOHLCV', 'createOrder', 'cancelOrder',
        'cancelAllOrders', 'setLeverage', 'setMarginMode', 'transfer',
        'fetchFundingRate'
    ]
    
    for method in methods_to_check:
        has_method = hasattr(exchange, method)
        has_key = method
        if method.startswith('fetch'): has_key = method[5].lower() + method[6:]
        if method.startswith('create'): has_key = 'create' + method[6:]
        if method.startswith('cancel'): has_key = 'cancel' + method[6:]
        
        support = exchange.has.get(has_key, 'Unknown')
        print(f"{method:20}: Available={str(has_method):5} | CCXT.has={support}")

if __name__ == "__main__":
    audit_bybit()
