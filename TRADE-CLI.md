# trade-cli is a command line wrapper for exchanges
It allows you to send commands to exchanges without worrying about the api of the exchange and how it works

# example

$ ./trade-cli entry --price 100000 --market btcusd --exchange hyperliquid --order-type limit --direction buy --size 1

Entry direction received: buy
Trade size: 1.0
Entry price: 100000.0
Order type: limit
Market: btcusd
Exchange: hyperliquid