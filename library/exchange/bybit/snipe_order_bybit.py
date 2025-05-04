import ccxt.async_support as ccxt # link against the asynchronous version of ccxt
import config
import json

# create a Bybit exchange object
exchange = ccxt.bybit({
    'apiKey': config.BYBIT_API_KEY,
    'secret': config.BYBIT_SECRET_KEY,
    'enableRateLimit': True,
    "options": {
        "defaultType": "margin",
    },
    'urls': {
        'api': {
            'public': 'https://api-testnet.bybit.com',
            'private': 'https://api-testnet.bybit.com',
        },
    },
})

# get account balance
balance = exchange.fetch_balance(params={'type': 'margin'})

# display perpetual account balance
perpetual_balance = balance['total']['USDT']
print(f"Perpetual Account Balance: {perpetual_balance}")
formatted_data = json.dumps(balance, indent=4)
print(formatted_data)

# display balance for each type
for key in balance:
    print(f"{key}: {balance[key]['total']}")

# load the markets
exchange.load_markets()

# set the order parameters
symbol = 'BTCUSDT'  # use Bybit symbol
amount = 1  # 1 contract (perpetual)
ticker = exchange.fetch_ticker(symbol)
price = ticker['last']  # current market price
stop_loss = 0.95 * price  # 5% stop loss
leverage = 10

# create the order
try:
    order = exchange.create_order(symbol, 'limit', 'buy', amount, price, {
        'leverage': leverage,
        'stop_loss': stop_loss,
    })
    print(order)
except Exception as e:
    print(str(e))

