from binance.client import Client
API_KEY = "sRybYz03CNAgl8NVmka05m9VDYLmftT6MmX35vTfJoC1JFNGurSMVwAoFoUJswhi"
SECRET_KEY = "GDop7L7GI9drgMfm9HAL5nOLBrQ5csaD35XQCUQyT03RBhIdwujpuxBD99T0Esoj"
client = Client(API_KEY, SECRET_KEY)

def get_current_price(symbol):
    ticker = client.futures_symbol_ticker(symbol=symbol)
    return float(ticker['price'])
