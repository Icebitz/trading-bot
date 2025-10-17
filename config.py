import os
import requests
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


def get_btc_price():
  url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
  response = requests.get(url).json()
  return response["price"]

def get_tao_price():
  url = "https://api.binance.com/api/v3/ticker/price?symbol=TAOUSDT"
  response = requests.get(url).json()
  return response["price"]

