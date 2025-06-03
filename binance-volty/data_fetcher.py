import time
from binance.client import Client
from prettyprinter import pprint
# API_KEY = "sRybYz03CNAgl8NVmka05m9VDYLmftT6MmX35vTfJoC1JFNGurSMVwAoFoUJswhi"
# SECRET_KEY = "GDop7L7GI9drgMfm9HAL5nOLBrQ5csaD35XQCUQyT03RBhIdwujpuxBD99T0Esoj"
# client = Client(API_KEY, SECRET_KEY)

# def get_current_price(symbol):
#     ticker = client.futures_symbol_ticker(symbol=symbol)
#     return float(ticker['price'])

from binance.um_futures import UMFutures

api = "7LqL2PLmneyyWWyWrbieWFAY8nzt3qA1O2XcyYedkkHwYxcNkKOgPq0Y70peGNew"
secret = "uhHavmCcjZ1K8xvxp9XZ9ZlwXt0wpK5SJ7CaY50lfomr3GGOBaoZJ1YeRHqJBA8V"

test_api = "zGvItNbcUPa0T4Dw9SlwY3t36AbjNo3pNC1i2F6q2qlHFjAqSayW09SMngS7C4bi"
test_secret = "HZvEpfssBg6aJY8wywtnbRA6bkoa7tmIKnVTV2eKcAiKlSY48Ak3U034ghWjRixm"

client = UMFutures(key=api, secret=secret)

def get_best_ask(symbol):
    try:
        depth = client.depth(symbol=symbol)
        best_ask = float(depth["asks"][0][0])
        return best_ask
    except Exception as e:
        print("Error fetching depth:", e)
        return None

def get_best_bid(symbol):
    try:
        depth = client.depth(symbol=symbol)
        best_bid = float(depth["bids"][0][0])
        return best_bid
    except Exception as e:
        print("Error fetching depth:", e)
        return None

def long_position_step(qty, leverage=1, symbol="BTCUSDC"):
    # Set leverage
    client.change_leverage(symbol=symbol, leverage=leverage)

    order_id = None
    last_price = None

    while True:
        # Get current ask price
        current_ask = round(get_best_ask(symbol), 2)
        target_price = round(current_ask - 0.10, 2)

        # Only act if price has changed
        if target_price != last_price:
            last_price = target_price

            # Cancel previous order if it exists
            if order_id:
                try:
                    client.cancel_order(symbol=symbol, orderId=order_id)
                except Exception as e:
                    print("Cancel error:", e)

            # Place new order at updated price
            try:
                order = client.new_order(
                    symbol=symbol,
                    side="BUY",
                    type="LIMIT",
                    quantity=qty,
                    timeInForce="GTC",
                    price=target_price
                )
                order_id = order["orderId"]
                print(f"Placed new order at {target_price}")
            except Exception as e:
                print("Order placement error:", e)
                time.sleep(1)
                continue

        # Check if order was filled
        try:
            positions = client.get_position_risk()
            if len(positions) != 0:
                client.cancel_open_orders(symbol=symbol, recvWindow=2000)
                break
            else:
                time.sleep(5)
                continue    
        except Exception as e:
            print(f"Error Getting Positions: {e}")
            break

def long_position(qty, leverage=1):
    client.change_leverage("BTCUSDC", leverage)
    order = client.new_order(
        symbol="BTCUSDC",
        side="BUY",
        type="LIMIT",
        quantity=qty,
        timeInForce="GTC",
        price=get_best_ask("BTCUSDC") - 0.10,
    )
    print(order)

def get_balance_usdc():
    response = client.balance(recvWindow=6000)
    pprint(response)


def get_ticker_usdc():
    tickers = []
    resp = client.ticker_price()
    pprint(resp)
    for elem in resp:
        if 'USDC' in elem['symbol']:
            tickers.append(elem['symbol'])
    return tickers

pprint(get_best_bid("BTCUSDC"))

def short_position(qty, leverage=1):
    client.change_leverage("BTCUSDC", leverage)
    order = client.new_order(
        symbol="BTCUSDC",
        side="SELL",
        type="LIMIT",
        quantity=qty,
        timeInForce="GTC",
        price=get_best_bid("BTCUSDC") + 0.10,
    )
    print(order)

short_position(0.001, leverage=20)
# def close_long_position():
#     positions = cm_futures_client.get_position_risk()