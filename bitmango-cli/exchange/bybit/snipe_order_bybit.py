import ccxt.async_support as ccxt # link against the asynchronous version of ccxt
import config
import json
from bitmango.output import display_message

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
from bitmango.messages import get_message
display_message('info', get_message("trade.perpetual_balance", balance=perpetual_balance))
formatted_data = json.dumps(balance, indent=4)
display_message('info', formatted_data)

# display balance for each type
for key in balance:
    if isinstance(balance[key], dict) and 'total' in balance[key]:
        display_message('info', get_message("trade.balance_asset_total", key=key, total=balance[key]['total']))

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
    display_message('info', json.dumps(order, indent=2))
except Exception as e:
    display_message('error', str(e))

