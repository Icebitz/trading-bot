import requests
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta
import pytz
import os
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Recorder:
    def __init__(self, symbol='BTCUSDT', interval=60, filename='data/btc_prices.csv'):
        self.symbol = symbol
        self.interval = interval
        self.filename = filename
        self.api_url = 'https://api.binance.com/api/v3/ticker/price'
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.last_log_time = 0
        self.log_interval = 1800
        
    def fetch_price(self):
        try:
            response = requests.get(self.api_url + '?symbol=' + self.symbol, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'price' not in data:
                raise ValueError("Price data not found in API response")
                
            price = float(data['price'])
            self.consecutive_failures = 0
            return price
            
        except Exception as e:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.error(f"API error (attempt {self.consecutive_failures}): {e}")
            return None
    
    def get_last_timestamp(self):
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                if not df.empty and 'timestamp' in df.columns:
                    last_timestamp = pd.to_datetime(df['timestamp'].iloc[-1])
                    return last_timestamp
        except Exception as e:
            logger.debug(f"Error reading last timestamp: {e}")
        return None
    
    # Removed complex gap check to keep background runner simple
    def check_and_fill_missing_data(self):
        return
    
    def detect_missing_periods(self):
        if not os.path.exists(self.filename):
            return []
        
        try:
            df = pd.read_csv(self.filename)
            if df.empty:
                return []
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            missing_periods = []
            for i in range(len(df) - 1):
                current_time = df.iloc[i]['timestamp']
                next_time = df.iloc[i + 1]['timestamp']
                expected_interval = timedelta(seconds=self.interval)
                actual_interval = next_time - current_time
                
                if actual_interval > expected_interval * 1.5:
                    missing_periods.append({
                        'start': current_time,
                        'end': next_time
                    })
            
            return missing_periods
        except Exception as e:
            logger.debug(f"Error detecting missing periods: {e}")
            return []
    
    # Historical recovery removed for simplicity
    def fetch_historical_data(self, start_time, end_time):
        return []
    
    def recover_missing_data(self):
        return
    
    def save_recovered_data(self, recovered_data):
        try:
            if not recovered_data:
                return
            
            df_recovered = pd.DataFrame(recovered_data)
            
            if os.path.exists(self.filename):
                existing_df = pd.read_csv(self.filename)
                existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
                
                combined_df = pd.concat([existing_df, df_recovered], ignore_index=True)
                combined_df = combined_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
            else:
                combined_df = df_recovered
            
            combined_df.to_csv(self.filename, index=False)
            if self.verbose:
                logger.info(f"Saved {len(recovered_data)} points to {self.filename}")
            
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def save_price(self):
        price = self.fetch_price()
        if price:
            jst = pytz.timezone('Asia/Tokyo')
            
            last_timestamp = self.get_last_timestamp()
            if last_timestamp:
                timestamp = last_timestamp + timedelta(minutes=1)
            else:
                timestamp = datetime.now(jst)
            
            timestamp = timestamp.replace(microsecond=0)
            
            df = pd.DataFrame({
                'timestamp': [timestamp],
                'price': [round(price, 2)]
            })
            
            try:
                existing_df = pd.read_csv(self.filename)
                df = pd.concat([existing_df, df], ignore_index=True)
            except FileNotFoundError:
                pass
            
            df.to_csv(self.filename, index=False)
            
            current_time = time.time()
            if (current_time - self.last_log_time) >= self.log_interval:
                logger.info(f"{self.symbol}: ${price:,.2f}")
                self.last_log_time = current_time
        else:
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.warning("Failed to fetch price data")
    
    def check_and_recover(self):
        return
    
    def start(self):
        self.save_price()
        schedule.every(self.interval).seconds.do(self.save_price)
        logger.info(f"Started {self.symbol} every {self.interval}s → {self.filename}")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopped by user")
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(5)


if __name__ == '__main__':
    import sys
    # Only two options: no arg (default file) or CSV path
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        filename = sys.argv[1]
    else:
        filename = 'data/btc_prices.csv'

    recorder = Recorder(symbol='BTCUSDT', interval=60, filename=filename)
    logger.info(f"Recording to {filename}")
    recorder.start()

