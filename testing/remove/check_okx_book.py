import ccxt
import json

def check_okx_book():
    exchange = ccxt.okx()
    book = exchange.fetch_order_book('BTC/USDT:USDT')
    print("OKX Asks Top 1 structure:")
    print(book['asks'][0])

if __name__ == "__main__":
    check_okx_book()
