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
    def __init__(self, symbol='BTCUSDT', interval=60, filename='../data/btc_prices.csv', verbose=True):
        self.symbol = symbol
        self.interval = interval  # seconds; use 60 for per-minute recording
        self.filename = filename
        self.api_url = 'https://api.binance.com/api/v3/ticker/price'
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.last_log_time = 0
        self.log_interval = 1800  # seconds
        self.verbose = verbose
        
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
            else:
                logger.debug(f"API error (attempt {self.consecutive_failures}): {e}")
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
        try:
            # Try absolute import first (works when running as a script)
            try:
                from modules.historical import fetch_minute_prices
            except Exception:
                # Fallback to relative import when used as a package
                from .historical import fetch_minute_prices
            return fetch_minute_prices(self.symbol, start_time, end_time)
        except Exception as e:
            logger.error(f"Historical fetch error: {e}")
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
        if price is None:
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.warning("Failed to fetch price data")
            return

        # Align to minute in JST
        jst = pytz.timezone('Asia/Tokyo')
        now_ts_jst = datetime.now(jst).replace(second=0, microsecond=0)
        now_ts = now_ts_jst.replace(tzinfo=None)

        # Build list of rows to write (backfill gaps if any)
        rows = []
        last_timestamp = self.get_last_timestamp()

        # Ensure output directory exists
        try:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        except Exception:
            pass

        if last_timestamp is None:
            # First record
            rows.append({'timestamp': now_ts, 'price': round(price, 2)})
        else:
            expected_next = (last_timestamp + timedelta(minutes=1)).replace(second=0, microsecond=0)

            if expected_next > now_ts:
                # System clock skew; still record current minute to avoid going backwards
                logger.warning(f"Clock skew: last={last_timestamp}, expected_next={expected_next}, now={now_ts}")
                rows.append({'timestamp': now_ts, 'price': round(price, 2)})
            else:
                # If there is a gap, fetch historical minute prices for missing minutes
                if expected_next < now_ts:
                    try:
                        historical_rows = self.fetch_historical_data(expected_next, now_ts)
                    except Exception:
                        historical_rows = []

                    if historical_rows:
                        for r in historical_rows:
                            try:
                                ts_jst = r['timestamp'].astimezone(jst).replace(second=0, microsecond=0)
                                ts_local = ts_jst.replace(tzinfo=None)
                                if ts_local < now_ts:
                                    rows.append({'timestamp': ts_local, 'price': round(float(r['price']), 2)})
                            except Exception:
                                continue
                    # If historical fetch failed, skip backfill to avoid repeating price

                # Always write the current minute value as the final row
                rows.append({'timestamp': now_ts, 'price': round(price, 2)})

        # Persist
        try:
            new_df = pd.DataFrame(rows)
            if os.path.exists(self.filename):
                existing_df = pd.read_csv(self.filename)
                if not existing_df.empty:
                    existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df

            # Enforce types: timestamp as datetime and price as numeric (float)
            combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
            combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce').round(2)
            combined_df = combined_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'])

            combined_df.to_csv(self.filename, index=False)
        except Exception as e:
            logger.error(f"Save error: {e}")
            return

        # Occasional log
        current_time = time.time()
        if (current_time - self.last_log_time) >= self.log_interval:
            logger.info(f"{self.symbol}: ${price:,.2f}")
            self.last_log_time = current_time
    
    def start(self):
        # Initial write aligns to current minute; subsequent writes every interval
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
        filename = '../data/btc_prices.csv'

    recorder = Recorder(symbol='BTCUSDT', interval=60, filename=filename, verbose=True)
    logger.info(f"Recording to {filename}")
    recorder.start()

