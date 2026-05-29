import ccxt
import math
import time

from bitmango.exchange.base_exchange import BaseExchange
from bitmango.messages import get_message

class SmartStopMexc(BaseExchange):
    def __init__(self, exchange, symbol):
        super().__init__(exchange, symbol)
        self.symbol = symbol # Set the symbol here
        self.exchange.options['defaultType'] = 'future'
        self.exchange.options['createMarketBuyOrderRequiresPrice'] = False
        self.exchange.options['createMarketSellOrderRequiresPrice'] = False

    def close_position(self, params={}):
        self.display_message('debug', get_message("trade.debug_entering_close_position", symbol=self.symbol))
        # Determine current position
        balance = self.exchange.fetch_balance({'type': 'future'})
        positions = balance.get('info', {}).get('data', {}).get('positions', [])
        current_position = None
        for position in positions:
            if position.get('symbol') == self.symbol:
                current_position = position
                break

        if not current_position or float(current_position.get('size', 0)) == 0:
            self.display_message('info', get_message("trade.no_open_position_to_close", symbol=self.symbol))
            return

        position_size = float(current_position['size'])
        side = 'sell' if position_size > 0 else 'buy'
        abs_position_size = abs(position_size)

        self.display_message('debug', get_message("trade.debug_current_pos_size", size=position_size, abs_size=abs_position_size, side=side))
        self.display_message('info', get_message("trade.attempt_close_contracts", amount=abs_position_size, symbol=self.symbol, side=side))

        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            market_price = ticker['last']
            self.display_message('debug', get_message("trade.debug_market_price", symbol=self.symbol, price=market_price))

            order_params = {'reduceOnly': True}
            order_params.update(params) # Merge any additional params from the caller

            self.display_message('debug', get_message("trade.debug_calling_create_order", symbol=self.symbol, type='market', side=side, amount=abs_position_size, price=market_price, params=order_params))
            order = self.exchange.create_order(
                self.symbol,
                'market',
                side,
                abs_position_size,
                market_price,
                params=order_params
            )
            self.display_message('success', get_message("trade.close_order_placed", order=order))
            return order
        except ccxt.NetworkError as e:
            self.display_message('error', get_message("trade.network_error_close", error=e))
        except ccxt.ExchangeError as e:
            self.display_message('error', get_message("trade.exchange_error_close", error=e))
        except Exception as e:
            self.display_message('error', get_message("trade.unexpected_error_close", error=e))
        return None

    def open_position(self, usd_amount, side, params={}):
        self.display_message('debug', get_message("trade.debug_entering_open_position", symbol=self.symbol, amount=usd_amount, side=side))
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            market_price = ticker['last']
            self.display_message('debug', get_message("trade.debug_market_price", symbol=self.symbol, price=market_price))

            # Convert USD amount to base asset quantity using calculate_contract_size
            # Assuming usd_amount is the total value in USDT for linear contracts
            base_asset_quantity = self.calculate_contract_size(usd_amount, market_price)
            if base_asset_quantity <= 0:
                self.display_message('error', get_message("trade.base_asset_quantity_error", amount=base_asset_quantity))
                return None

            self.display_message('debug', get_message("trade.debug_usd_to_base_quantity", usd=usd_amount, base=base_asset_quantity))
            self.display_message('debug', get_message("trade.debug_calling_create_order", symbol=self.symbol, type='market', side=side, amount=base_asset_quantity, price=market_price, params=params))
            order = self.exchange.create_order(
                self.symbol,
                'market',
                side,
                base_asset_quantity,
                market_price,
                params=params
            )
            self.display_message('success', get_message("trade.open_order_placed", order=order))
            return order
        except ccxt.NetworkError as e:
            self.display_message('error', get_message("trade.network_error_open", error=e))
        except ccxt.ExchangeError as e:
            self.display_message('error', get_message("trade.exchange_error_open", error=e))
        except Exception as e:
            self.display_message('error', get_message("trade.unexpected_error_open", error=e))
        return None

    def place_smart_stop_market_order(self, trigger_price, stop_loss_price, take_profit_price, order_type, side, amount):
        # This function would contain the logic for placing a smart stop market order
        # based on the provided parameters. This is a placeholder.
        self.display_message('info', get_message("trade.placing_smart_stop_header", symbol=self.symbol))
        self.display_message('info', get_message("trade.smart_stop_trigger", price=trigger_price))
        self.display_message('info', get_message("trade.smart_stop_sl", price=stop_loss_price))
        self.display_message('info', get_message("trade.smart_stop_tp", price=take_profit_price))
        self.display_message('info', get_message("trade.smart_stop_type", type=order_type))
        self.display_message('info', get_message("trade.smart_stop_side", side=side))
        self.display_message('info', get_message("trade.smart_stop_amount", amount=amount))
        # Implement actual order placement logic here
        pass

    def calculate_contract_size(self, usd_amount, price):
        # For MEXC USDT linear contracts, the amount parameter in create_order is the quantity of the base asset.
        # So, if usd_amount is in USDT, and price is USDT per base asset, then quantity = usd_amount / price
        self.display_message('debug', get_message("trade.debug_calc_contract_size", amount=usd_amount, price=price))
        if price is None or price == 0:
            self.display_message('error', get_message("trade.error_price_zero_calc"))
            return 0
        quantity = usd_amount / price
        self.display_message('debug', get_message("trade.debug_calc_quantity", quantity=quantity))
        return quantity

    def get_contract_size(self, symbol):
        # This method would fetch contract size details if needed for specific calculations
        # For MEXC USDT linear contracts, the 'amount' in orders is the quantity of the base asset.
        # So, the contract size is effectively 1 unit of the base asset.
        # This function might be more relevant for inverse contracts or if MEXC had fixed contract sizes.
        return 1 # Assuming 1 unit of base asset for linear contracts
