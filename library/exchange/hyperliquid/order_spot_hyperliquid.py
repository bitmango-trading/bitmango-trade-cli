import sys
import ccxt
from library.exchange.functions import format_symbol, format_direction  # Import functions from functions.py

from eth_account.signers.local import LocalAccount
import eth_account
import json
import time 
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import pandas as pd
import datetime
import schedule 
import requests 

def execute(exchange, args):
    """
    args.direction   # 'buy' or 'long'
    args.size        # float
    args.price       # float or None
    args.order_type  # 'market' or 'limit'
    args.pair        # str, e.g. 'btcusdt' or 'BTC/USDT'
    args.no_confirm  # bool
    args.sandbox     # bool
    """

    # Build symbol and parameters
    coin = args.pair.split("-")[0].upper() + '-PERP'
    is_buy = true
    order_type = args.order_type  # 'limit' or 'market'
    sz = args.size
    price = args.price if type_ == "limit" else None
    
    symbol = format_symbol(args.pair, format_type='slash')
    side = format_direction(args.direction, 'buy')
    limit = 1000 
    max_loss = -1
    target = 5
    pos_size = 200
    leverage = 10
    vol_multiplier = 3
    rounding = 4

    # Send the order
    try:
        if type_ == "market":
            order = exchange.create_market_order(coin, is_buy, sz)
        else:
            order = exchange.create_limit_order(coin, is_buy, sz)
        print("✅ Order executed:") # If we reach here, the order was successful
        print(order)
    except ccxt.BaseError as e:
        # Print out the full error message
        print(f"❌ Order failed: {str(e)}")

        # Check if the exception has a 'response' attribute, which contains the full error response
        if hasattr(e, 'response'):
            try:
                # If available, print the response
                print(f"Full error response from {args.exchange}:")
                print(e.response)  # This will give you the raw response from the API
            except Exception as inner_e:
                print("❌ Could not parse error response:", str(inner_e))
        
        # You can also log additional information like the HTTP status code (if available)
        if hasattr(e, 'http_status'):
            print("HTTP Status Code:", e.http_status)

        sys.exit(1)

    if order:  # This checks if the order was created successfully
        print("✅ Order executed:")
        print(order)


def get_sz_px_decimals(symbol):

    '''
    this is succesfully returns Size decimals and Price decimals

    this outputs the size decimals for a given symbol
    which is - the SIZE you can buy or sell at
    ex. if sz decimal == 1 then you can buy/sell 1.4
    if sz decimal == 2 then you can buy/sell 1.45
    if sz decimal == 3 then you can buy/sell 1.456

    if size isnt right, we get this error. to avoid it use the sz decimal func
    {'error': 'Invalid order size'}
    '''
    url = 'https://api.hyperliquid.xyz/info'
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'meta'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # Success
        data = response.json()
        #print(data)
        symbols = data['universe']
        symbol_info = next((s for s in symbols if s['name'] == symbol), None)
        if symbol_info:
            sz_decimals = symbol_info['szDecimals']
            
        else:
            print('Symbol not found')
    else:
        # Error
        print('Error:', response.status_code)

    ask = ask_bid(symbol)[0]
    #print(f'this is the ask {ask}')

    # Compute the number of decimal points in the ask price
    ask_str = str(ask)
    if '.' in ask_str:
        px_decimals = len(ask_str.split('.')[1])
    else:
        px_decimals = 0

    print(f'{symbol} this is the price {sz_decimals} decimal(s)')

    return sz_decimals, px_decimals

def limit_order(coin: str, is_buy: bool, sz: float, limit_px: float, reduce_only: bool = False):
    account: LocalAccount = eth_account.Account.from_key(key)
    exchange = Exchange(account, constants.MAINNET_API_URL)
    rounding = get_sz_px_decimals(coin)[0]
    sz = round(sz,rounding)
    # limit_px = round(limit_px,rounding)
    print(f'placing limit order for {coin} {sz} @ {limit_px}')
    order_result = exchange.order(coin, is_buy, sz, limit_px, {"limit": {"tif": "Gtc"}}, reduce_only=reduce_only)

    if is_buy == True:
        print(f"limit BUY order placed thanks moon, resting: {order_result['response']['data']['statuses'][0]}")
    else:
        print(f"limit SELL order placed thanks moon, resting: {order_result['response']['data']['statuses'][0]}")

    return order_result



limit_order(symbol, True, pos_size, bid) # buy order