import ccxt

def get_account_summary(api_key, api_secret):
  """Fetches account balances and positions (spot and margin) for Binance exchange.

  Args:
    api_key (str): Your Binance API key.
    api_secret (str): Your Binance API secret.

  Returns:
    dict: A dictionary containing spot and margin account balances and positions.
  """
  exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True
  })

  # Fetch spot account balances
  spot_balances = exchange.fetch_balance(params={'type': 'SPOT'})

  # Fetch margin account balances
  margin_balances = exchange.fetch_balance(params={'type': 'MARGIN'})

  # Fetch current positions (includes both spot and margin positions)
  positions = exchange.fetch_positions()

  return {
    'spot': spot_balances,
    'margin': margin_balances,
    'positions': positions
  }

