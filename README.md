# bitmango-trade-cli
command line wrapper for crypto trading exchanges

It allows you to send THE SAME commands to exchanges without worrying about the api of the exchange and how it works

# example

$ ./trade-cli entry --price 100000 --pair ltc-usd --exchange hyperliquid --order-type limit --direction buy --size 1

Entry direction received: buy
Trade size: 1.0
Entry price: 100.0
Order type: limit
Market: ltc-usd
Exchange: hyperliquid
