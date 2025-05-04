'''This is the parent library that you call
This file will call the appropriate file based on the exchange
The idea of this is so that you don't have to rewrite the code all the time.
Instead it's modular

e.g.

if the exchange being used is binance
send the order data to : 
- order_buy_binance.py

if the exchange is mexc
send the order data to :
- order_buy_mexc.py
'''