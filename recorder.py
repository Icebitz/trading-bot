import requests
import pandas as pd
import schedule
import time
from datetime import datetime


class Recorder:
    def __init__(self, symbol='BTCUSDT', interval=60, filename='btc_price_data.csv'):
        self.symbol = symbol
        self.interval = interval
        self.filename = filename
        # self.api_url = 'https://api.mexc.com/api/v3/ticker/price'
        self.api_url = 'https://api.binance.com/api/v3/ticker/price'
        
    def fetch_price(self):
        try:
            response = requests.get(self.api_url + '?symbol=' + self.symbol)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def save_price(self):
        price = self.fetch_price()
        if price:
            timestamp = datetime.now()
            df = pd.DataFrame({
                'timestamp': [timestamp],
                'price': [price]
            })
            
            try:
                existing_df = pd.read_csv(self.filename)
                df = pd.concat([existing_df, df], ignore_index=True)
            except FileNotFoundError:
                pass
            
            df.to_csv(self.filename, index=False)
            print(f"{timestamp} - BTC Price: ${price}")
    
    def start(self):
        self.save_price()
        schedule.every(self.interval).seconds.do(self.save_price)
        
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    recorder = Recorder(symbol='BTCUSDT', interval=60)
    recorder.start()

