import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import sys


class PriceViewer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        
        if not os.path.exists(self.data_dir):
            print(f"Error: Data directory '{self.data_dir}' does not exist.")
            print("Please run price_recorder.py first to collect data.")
            sys.exit(1)
    
    def load_data(self, symbol):
        """Load price data from CSV file."""
        filepath = os.path.join(self.data_dir, f"{symbol.lower()}_price_history.csv")
        
        if not os.path.exists(filepath):
            print(f"Error: No data file found for {symbol}")
            return None
        
        df = pd.read_csv(filepath)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    
    def plot_single_token(self, symbol, tail=None):
        """
        Plot price history for a single token.
        
        Args:
            symbol: Token symbol (e.g., 'BTC', 'TAO')
            tail: Number of latest records to display (None for all)
        """
        df = self.load_data(symbol)
        if df is None or len(df) == 0:
            print(f"No data available for {symbol}")
            return
        
        if tail:
            df = df.tail(tail)
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['datetime'], df['price'], linewidth=2, marker='o', markersize=4)
        
        plt.title(f'{symbol} Price History', fontsize=16, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Price (USD)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.gcf().autofmt_xdate()
        
        # Add statistics
        current_price = df['price'].iloc[-1]
        min_price = df['price'].min()
        max_price = df['price'].max()
        avg_price = df['price'].mean()
        
        stats_text = f'Current: ${current_price:.2f}\n'
        stats_text += f'Min: ${min_price:.2f}\n'
        stats_text += f'Max: ${max_price:.2f}\n'
        stats_text += f'Avg: ${avg_price:.2f}'
        
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor='wheat', alpha=0.5), fontsize=10)
        
        plt.tight_layout()
        plt.show()
    
    def plot_multiple_tokens(self, symbols, tail=None, normalize=False):
        """
        Plot price history for multiple tokens on the same graph.
        
        Args:
            symbols: List of token symbols
            tail: Number of latest records to display (None for all)
            normalize: If True, normalize prices to percentage change from start
        """
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for symbol in symbols:
            df = self.load_data(symbol)
            if df is None or len(df) == 0:
                print(f"No data available for {symbol}")
                continue
            
            if tail:
                df = df.tail(tail)
            
            if normalize:
                # Normalize to percentage change from first value
                first_price = df['price'].iloc[0]
                df['normalized_price'] = ((df['price'] - first_price) / first_price) * 100
                ax.plot(df['datetime'], df['normalized_price'], 
                        linewidth=2, marker='o', markersize=3, label=symbol)
            else:
                ax.plot(df['datetime'], df['price'], 
                        linewidth=2, marker='o', markersize=3, label=symbol)
        
        title = 'Token Price Comparison'
        ylabel = 'Price Change (%)' if normalize else 'Price (USD)'
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.show()
    
    def get_statistics(self, symbol):
        """Display statistics for a token."""
        df = self.load_data(symbol)
        if df is None or len(df) == 0:
            print(f"No data available for {symbol}")
            return
        
        print(f"\n{'='*50}")
        print(f"Statistics for {symbol}")
        print(f"{'='*50}")
        print(f"Total records: {len(df)}")
        print(f"First record: {df['datetime'].iloc[0]}")
        print(f"Last record: {df['datetime'].iloc[-1]}")
        print(f"\nPrice Statistics:")
        print(f"  Current: ${df['price'].iloc[-1]:.2f}")
        print(f"  Min: ${df['price'].min():.2f}")
        print(f"  Max: ${df['price'].max():.2f}")
        print(f"  Average: ${df['price'].mean():.2f}")
        print(f"  Std Dev: ${df['price'].std():.2f}")
        
        # Calculate change from first to last
        price_change = df['price'].iloc[-1] - df['price'].iloc[0]
        price_change_pct = (price_change / df['price'].iloc[0]) * 100
        print(f"  Change: ${price_change:.2f} ({price_change_pct:+.2f}%)")
        print(f"{'='*50}\n")


def main():
    """Main function with example usage."""
    viewer = PriceViewer(data_dir="data")
    
    # Example: Display statistics
    viewer.get_statistics('BTC')
    viewer.get_statistics('TAO')
    
    # Example: Plot single token (all data)
    # viewer.plot_single_token('BTC')
    
    # Example: Plot single token (last 100 records)
    # viewer.plot_single_token('BTC', tail=100)
    
    # Example: Plot multiple tokens (not normalized)
    # viewer.plot_multiple_tokens(['BTC', 'TAO'])
    
    # Example: Plot multiple tokens (normalized to show % change)
    viewer.plot_multiple_tokens(['BTC', 'TAO'], normalize=True)


if __name__ == "__main__":
    main()

