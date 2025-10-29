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
    def __init__(self, symbol='BTCUSDT', interval=60, filename='data/btc_prices.csv', verbose=False):
        self.symbol = symbol
        self.interval = interval
        self.filename = filename
        self.api_url = 'https://api.binance.com/api/v3/ticker/price'
        self.historical_api_url = 'https://api.binance.com/api/v3/klines'
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.verbose = verbose
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
            if self.verbose:
                logger.error(f"Error reading last timestamp: {e}")
        return None
    
    def check_and_fill_missing_data(self):
        last_timestamp = self.get_last_timestamp()
        if not last_timestamp:
            if self.verbose:
                logger.info("No existing data found, starting fresh")
            return
        
        jst = pytz.timezone('Asia/Tokyo')
        current_time = datetime.now(jst)
        time_diff = current_time - last_timestamp
        
        if self.verbose:
            logger.debug(f"Last recorded: {last_timestamp}")
            logger.debug(f"Current time: {current_time}")
            logger.debug(f"Time diff: {time_diff}")
        
        expected_interval = timedelta(seconds=self.interval)
        if time_diff > expected_interval * 1.5:
            logger.warning(f"Gap detected: {time_diff.total_seconds()/60:.1f}min missing")
            
            recovered_data = self.fetch_historical_data(last_timestamp, current_time)
            if recovered_data:
                self.save_recovered_data(recovered_data)
                logger.info(f"Recovered {len(recovered_data)} data points")
            else:
                logger.warning("No historical data available")
        elif self.verbose:
            logger.debug("No significant gap detected")
    
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
            if self.verbose:
                logger.error(f"Error detecting missing periods: {e}")
            return []
    
    def fetch_historical_data(self, start_time, end_time):
        try:
            start_ms = int(start_time.timestamp() * 1000)
            end_ms = int(end_time.timestamp() * 1000)
            
            params = {
                'symbol': self.symbol,
                'interval': '1m',
                'startTime': start_ms,
                'endTime': end_ms,
                'limit': 1000
            }
            
            response = requests.get(self.historical_api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return []
            
            historical_prices = []
            jst = pytz.timezone('Asia/Tokyo')
            
            for kline in data:
                timestamp = datetime.fromtimestamp(kline[0] / 1000, tz=jst)
                timestamp = timestamp.replace(microsecond=0)
                price = float(kline[4])
                
                historical_prices.append({
                    'timestamp': timestamp,
                    'price': price
                })
            
            return historical_prices
            
        except Exception as e:
            logger.error(f"Historical data error: {e}")
            return []
    
    def recover_missing_data(self):
        if self.verbose:
            logger.info("Starting data recovery...")
        
        missing_periods = self.detect_missing_periods()
        if not missing_periods:
            return
        
        all_recovered_data = []
        for period in missing_periods:
            recovered_data = self.fetch_historical_data(period['start'], period['end'])
            all_recovered_data.extend(recovered_data)
        
        if all_recovered_data:
            self.save_recovered_data(all_recovered_data)
            logger.info(f"Recovered {len(all_recovered_data)} data points")
        else:
            logger.warning("No data recovered")
    
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
                'price': [price]
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
        if self.consecutive_failures >= self.max_consecutive_failures:
            logger.warning(f"API failures ({self.consecutive_failures}), recovering...")
            
            self.recover_missing_data()
            
            self.consecutive_failures = 0
            if self.verbose:
                logger.info("Recovery completed")
    
    def start(self):
        self.check_and_fill_missing_data()
        self.save_price()
        schedule.every(self.interval).seconds.do(self.save_price)
        schedule.every(5).minutes.do(self.check_and_recover)
        
        logger.info(f"Started: {self.symbol} every {self.interval}s")
        if self.verbose:
            logger.info("Data recovery enabled")
        
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
    
    test_csv = None
    verbose = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check':
            if len(sys.argv) > 2:
                test_csv = sys.argv[2]
            recorder = Recorder(symbol='BTCUSDT', interval=60, filename=test_csv or 'data/btc_prices.csv', verbose=False)
            if verbose:
                logger.info("Checking for missing data...")
            recorder.check_and_fill_missing_data()
        elif sys.argv[1] == '--quiet':
            verbose = False
            if len(sys.argv) > 2 and sys.argv[2].endswith('.csv'):
                test_csv = sys.argv[2]
            recorder = Recorder(symbol='BTCUSDT', interval=60, filename=test_csv or 'data/btc_prices.csv', verbose=verbose)
            logger.info("Starting price recorder in quiet mode...")
            recorder.start()
        elif sys.argv[1].endswith('.csv'):
            test_csv = sys.argv[1]
            recorder = Recorder(symbol='BTCUSDT', interval=60, filename=test_csv, verbose=verbose)
            if verbose:
                logger.info(f"Starting with test file: {test_csv}")
            recorder.start()
        else:
            print("Usage: python3 recorder.py [--check|--quiet] [test_file.csv]")
            print("Examples:")
            print("  python3 recorder.py                    # Use default data/btc_prices.csv")
            print("  python3 recorder.py test_data.csv       # Use test_data.csv for testing")
            print("  python3 recorder.py --check            # Check default file")
            print("  python3 recorder.py --check test.csv  # Check test file")
            print("  python3 recorder.py --quiet            # Run in quiet mode (minimal logging)")
    else:
        recorder = Recorder(symbol='BTCUSDT', interval=60, verbose=verbose)
        if verbose:
            logger.info("Starting price recorder...")
        recorder.start()

