import csv
import time
from datetime import datetime
import os
import sys
from config import get_btc_price, get_tao_price


class PriceRecorder:
    def __init__(self, symbols=None, interval=5, data_dir="data"):
        """
        Initialize the price recorder.
        
        Args:
            symbols: List of symbols to track (e.g., ['BTC', 'TAO'])
            interval: Time interval in seconds between price fetches
            data_dir: Directory to store CSV files
        """
        self.symbols = symbols or ['BTC', 'TAO']
        self.interval = interval
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Map symbols to their respective price functions
        self.price_functions = {
            'BTC': get_btc_price,
            'TAO': get_tao_price
        }
        
        # Initialize CSV files with headers if they don't exist
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Create CSV files with headers if they don't exist."""
        for symbol in self.symbols:
            filepath = self._get_filepath(symbol)
            if not os.path.exists(filepath):
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'datetime', 'symbol', 'price'])
                print(f"Created new CSV file: {filepath}")
    
    def _get_filepath(self, symbol):
        """Get the filepath for a symbol's CSV file."""
        return os.path.join(self.data_dir, f"{symbol.lower()}_price_history.csv")
    
    def fetch_and_record_price(self, symbol):
        """Fetch current price and save to CSV."""
        try:
            price_func = self.price_functions.get(symbol)
            if not price_func:
                print(f"No price function found for {symbol}")
                return None
            
            price = price_func()
            timestamp = time.time()
            dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # Append to CSV
            filepath = self._get_filepath(symbol)
            with open(filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, dt, symbol, price])
            
            print(f"[{dt}] {symbol}: ${price}")
            return float(price)
            
        except Exception as e:
            print(f"Error fetching {symbol} price: {e}")
            return None
    
    def record_continuously(self):
        """Record prices continuously at the specified interval."""
        print(f"Starting price recording for {', '.join(self.symbols)}")
        print(f"Recording interval: {self.interval} seconds")
        print(f"Data directory: {self.data_dir}")
        print("Press Ctrl+C to stop...\n")
        
        try:
            while True:
                for symbol in self.symbols:
                    self.fetch_and_record_price(symbol)
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\nRecording stopped by user.")
            print(f"Data saved in: {self.data_dir}/")
            sys.exit(0)


def main():
    """Main function to run the price recorder."""
    # Configure recording parameters
    SYMBOLS = ['BTC', 'TAO']  # Add more symbols as needed
    INTERVAL = 5  # seconds between recordings
    DATA_DIR = "data"
    
    recorder = PriceRecorder(symbols=SYMBOLS, interval=INTERVAL, data_dir=DATA_DIR)
    recorder.record_continuously()


if __name__ == "__main__":
    main()

