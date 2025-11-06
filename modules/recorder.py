import requests
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta
import pytz
import os
import logging
from typing import Optional, Dict, List
from historical import fetch_minute_prices

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Recorder:
    def __init__(self, symbol='BTCUSDT', interval=60, filename='data/btc_prices.csv', verbose=True):
        self.symbol = symbol
        self.interval = interval  # seconds; use 60 for per-minute recording
        self.dirname = os.path.dirname(__file__)
        self.filename = os.path.join(os.path.dirname(self.dirname), filename)
        self.api_url = 'https://api.binance.com/api/v3/ticker/price'
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.last_log_time = 0
        self.log_interval = 1800  # seconds
        self.verbose = verbose
        
        # Cache timezone object
        self.jst = pytz.timezone('Asia/Tokyo')
        
        # Use session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TradingBot/1.0'})
        
        # Cache last timestamp to avoid repeated file reads
        self._last_timestamp_cache: Optional[datetime] = None
        self._last_timestamp_file_mtime: Optional[float] = None
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        
    def fetch_price(self) -> Optional[float]:
        """Fetch current price from Binance API."""
        try:
            params = {'symbol': self.symbol}
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'price' not in data:
                raise ValueError("Price data not found in API response")
            price = float(data['price'])
            self.consecutive_failures = 0
            return price
        except (requests.RequestException, ValueError, KeyError) as e:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.error(f"API error (attempt {self.consecutive_failures}): {e}")
            else:
                logger.debug(f"API error (attempt {self.consecutive_failures}): {e}")
            return None
    
    def get_last_timestamp(self) -> datetime:
        """Get the last timestamp from CSV file with caching."""
        now_ts_jst = datetime.now(self.jst).replace(second=0, microsecond=0)
        now_ts = now_ts_jst.replace(tzinfo=None)

        # Check if file exists and get modification time
        if not os.path.exists(self.filename):
            self._last_timestamp_cache = now_ts
            return now_ts
        
        file_mtime = os.path.getmtime(self.filename)
        
        # Use cache if file hasn't changed
        if (self._last_timestamp_cache is not None and 
            self._last_timestamp_file_mtime == file_mtime):
            return self._last_timestamp_cache

        try:
            # Check if file is empty
            if os.path.getsize(self.filename) == 0:
                self._last_timestamp_cache = now_ts
                return now_ts
            
            # Read CSV and get last timestamp efficiently
            df = pd.read_csv(self.filename)
            if not df.empty and 'timestamp' in df.columns:
                last_timestamp = pd.to_datetime(df['timestamp'].iloc[-1])
                # Ensure timezone-naive
                if hasattr(last_timestamp, 'tz') and last_timestamp.tz is not None:
                    result = last_timestamp.tz_localize(None)
                elif hasattr(last_timestamp, 'tzinfo') and last_timestamp.tzinfo is not None:
                    result = last_timestamp.replace(tzinfo=None)
                else:
                    result = last_timestamp
                # Convert to Python datetime if it's a pandas Timestamp
                if isinstance(result, pd.Timestamp):
                    result = result.to_pydatetime()
                self._last_timestamp_cache = result
                self._last_timestamp_file_mtime = file_mtime
                return result
        except (pd.errors.EmptyDataError, pd.errors.ParserError, KeyError, IndexError, OSError) as e:
            logger.debug(f"Error reading last timestamp: {e}")
        
        self._last_timestamp_cache = now_ts
        return now_ts
    
    def detect_missing_periods(self) -> List[Dict]:
        """Detect missing time periods in the data using vectorized operations."""
        if not os.path.exists(self.filename):
            return []
        
        try:
            # Check if file is empty
            if os.path.getsize(self.filename) == 0:
                return []
            
            df = pd.read_csv(self.filename)
            if df.empty or 'timestamp' not in df.columns:
                return []
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Ensure all timestamps are timezone-naive
            if df['timestamp'].dt.tz is not None:
                df['timestamp'] = df['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            if len(df) < 2:
                return []
            
            # Vectorized calculation of intervals
            expected_interval = timedelta(seconds=self.interval)
            time_diffs = df['timestamp'].diff().shift(-1)
            threshold = expected_interval * 1.5
            
            # Find gaps using vectorized operations
            gaps = time_diffs > threshold
            gap_indices = df[gaps].index.tolist()
            
            missing_periods = []
            for idx in gap_indices:
                if idx < len(df) - 1:
                    missing_periods.append({
                        'start': df.iloc[idx]['timestamp'],
                        'end': df.iloc[idx + 1]['timestamp']
                    })
            
            return missing_periods
        except Exception as e:
            logger.debug(f"Error detecting missing periods: {e}")
            return []
    
    def fetch_historical_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Fetch historical minute prices for the given time range."""
        try:
            return fetch_minute_prices(self.symbol, start_time, end_time, session=self.session)
        except Exception as e:
            logger.error(f"Historical fetch error: {e}")
            return []
    
    def save_recovered_data(self, recovered_data: List[Dict]) -> None:
        """Save recovered historical data to CSV."""
        if not recovered_data:
            return
        
        try:
            df_recovered = pd.DataFrame(recovered_data)
            df_recovered['timestamp'] = pd.to_datetime(df_recovered['timestamp'])
            # Ensure all timestamps are timezone-naive
            if df_recovered['timestamp'].dt.tz is not None:
                df_recovered['timestamp'] = df_recovered['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)
            
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                try:
                    existing_df = pd.read_csv(self.filename)
                    if not existing_df.empty and 'timestamp' in existing_df.columns:
                        existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
                        # Ensure all timestamps are timezone-naive
                        if existing_df['timestamp'].dt.tz is not None:
                            existing_df['timestamp'] = existing_df['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)
                        
                        combined_df = pd.concat([existing_df, df_recovered], ignore_index=True)
                        combined_df = combined_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'], keep='last')
                    else:
                        combined_df = df_recovered
                except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                    logger.debug(f"CSV file is empty or invalid, using recovered data only: {e}")
                    combined_df = df_recovered
            else:
                combined_df = df_recovered
            
            # Format price to always show 2 decimal places
            combined_df['price'] = combined_df['price'].apply(lambda x: f'{float(x):.2f}')
            combined_df.to_csv(self.filename, index=False)
            # Invalidate cache after write
            self._last_timestamp_cache = None
            self._last_timestamp_file_mtime = None
            
            if self.verbose:
                logger.info(f"Saved {len(recovered_data)} points to {self.filename}")
            
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def save_price(self) -> None:
        """Fetch and save current price, backfilling gaps if necessary."""
        price = self.fetch_price()
        if price is None:
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.warning("Failed to fetch price data")
            return

        # Align to minute in JST
        now_ts_jst = datetime.now(self.jst).replace(second=0, microsecond=0)
        now_ts = now_ts_jst.replace(tzinfo=None)

        # Build list of rows to write (backfill gaps if any)
        rows = []
        last_timestamp = self.get_last_timestamp()
        if self.verbose:
            logger.debug(f"Last timestamp: {last_timestamp}")

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
                    if historical_rows:
                        for r in historical_rows:
                            try:
                                # Ensure timestamp is timezone-aware, convert to JST, then make naive
                                ts = r['timestamp']
                                if ts.tzinfo is None:
                                    ts = ts.replace(tzinfo=pytz.UTC)
                                ts_jst = ts.astimezone(self.jst).replace(second=0, microsecond=0)
                                ts_local = ts_jst.replace(tzinfo=None)
                                if ts_local < now_ts:
                                    rows.append({'timestamp': ts_local, 'price': round(float(r['price']), 2)})
                            except (KeyError, ValueError, AttributeError) as e:
                                logger.debug(f"Skipping invalid historical row: {e}")
                                continue
                except Exception as e:
                    logger.debug(f"Historical fetch failed: {e}")

            # Always write the current minute value as the final row
            rows.append({'timestamp': now_ts, 'price': round(price, 2)})

        # Persist efficiently
        if rows:
            try:
                new_df = pd.DataFrame(rows)
                new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
                # Ensure all timestamps are timezone-naive
                if new_df['timestamp'].dt.tz is not None:
                    new_df['timestamp'] = new_df['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)
                new_df['price'] = pd.to_numeric(new_df['price'], errors='coerce').round(2)
                
                if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                    try:
                        existing_df = pd.read_csv(self.filename)
                        if not existing_df.empty and 'timestamp' in existing_df.columns:
                            existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
                            # Ensure all timestamps are timezone-naive
                            if existing_df['timestamp'].dt.tz is not None:
                                existing_df['timestamp'] = existing_df['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)
                            existing_df['price'] = pd.to_numeric(existing_df['price'], errors='coerce')
                            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                        else:
                            combined_df = new_df
                    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                        logger.debug(f"CSV file is empty or invalid, creating new: {e}")
                        combined_df = new_df
                else:
                    combined_df = new_df

                # Sort and remove duplicates (keep last occurrence)
                combined_df = combined_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'], keep='last')
                # Format price to always show 2 decimal places
                combined_df['price'] = combined_df['price'].apply(lambda x: f'{float(x):.2f}')
                combined_df.to_csv(self.filename, index=False)
                
                # Invalidate cache after write
                self._last_timestamp_cache = None
                self._last_timestamp_file_mtime = None
                
            except Exception as e:
                logger.error(f"Save error: {e}")
                return

        # Occasional log
        current_time = time.time()
        if (current_time - self.last_log_time) >= self.log_interval:
            logger.info(f"{self.symbol}: ${price:,.2f}")
            self.last_log_time = current_time
    
    def start(self) -> None:
        """Start the recording loop."""
        # Initial write aligns to current minute; subsequent writes every interval
        self.save_price()
        schedule.every(self.interval).seconds.do(self.save_price)
        logger.info(f"Started {self.symbol} every {self.interval}s → {self.filename}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopped by user")
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            raise
        finally:
            # Clean up session
            self.session.close()


if __name__ == '__main__':
    import sys
    # Only two options: no arg (default file) or CSV path
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        filename = sys.argv[1]
    else:
        filename = 'data/btc_prices.csv'
        
    logger.info(f"Filename: {filename}")
    recorder = Recorder(symbol='BTCUSDT', interval=60, filename=filename, verbose=True)
    logger.info(f"Recording to {filename}")
    recorder.start()

