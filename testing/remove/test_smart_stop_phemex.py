import argparse
from bitmango_free.exchange.phemex.smart_stop_phemex import SmartStopPhemex

def main():
    parser = argparse.ArgumentParser(description='Test Phemex smart stop logic.')
    parser.add_argument('--pair', type=str, default='BTC/USDT', help='The trading pair to use.')
    parser.add_argument('--sandbox', action='store_true', help='Use the testnet.')
    args = parser.parse_args()

    # Create a SmartStopPhemex instance
    smart_stop = SmartStopPhemex(args)

    # Run the smart stop logic
    smart_stop.run()

if __name__ == '__main__':
    main()
