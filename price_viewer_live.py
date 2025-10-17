import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import os
import sys


class LivePriceViewer:
    def __init__(self, symbols=None, data_dir="data", update_interval=5000):
        self.symbols = symbols or ['BTC', 'TAO']
        self.data_dir = data_dir
        self.update_interval = update_interval
        
        if not os.path.exists(self.data_dir):
            print(f"Error: Data directory '{self.data_dir}' does not exist.")
            print("Please run price_recorder.py first to collect data.")
            sys.exit(1)
        
        self.fig, self.axes = plt.subplots(len(self.symbols), 1, 
                                            figsize=(12, 5*len(self.symbols)))
        if len(self.symbols) == 1:
            self.axes = [self.axes]
        
        plt.subplots_adjust(hspace=0.4)
    
    def load_data(self, symbol):
        """Load price data from CSV file."""
        filepath = os.path.join(self.data_dir, f"{symbol.lower()}_price_history.csv")
        
        if not os.path.exists(filepath):
            return None
        
        try:
            df = pd.read_csv(filepath)
            df['datetime'] = pd.to_datetime(df['datetime'])
            return df
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")
            return None
    
    def update_plot(self, frame):
        """Update plot with latest data."""
        for idx, symbol in enumerate(self.symbols):
            ax = self.axes[idx]
            ax.clear()
            
            df = self.load_data(symbol)
            if df is None or len(df) == 0:
                ax.text(0.5, 0.5, f'No data available for {symbol}',
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes)
                continue
            
            # Plot last 100 points (or all if less than 100)
            df_plot = df.tail(100)
            
            ax.plot(df_plot['datetime'], df_plot['price'], 
                   linewidth=2, marker='o', markersize=4, color='#2E86AB')
            
            # Title and labels
            current_price = df_plot['price'].iloc[-1]
            last_time = df_plot['datetime'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
            ax.set_title(f'{symbol} - ${current_price:.2f} (Last: {last_time})', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Time', fontsize=11)
            ax.set_ylabel('Price (USD)', fontsize=11)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            self.fig.autofmt_xdate()
            
            # Add statistics box
            min_price = df_plot['price'].min()
            max_price = df_plot['price'].max()
            avg_price = df_plot['price'].mean()
            
            stats_text = f'Min: ${min_price:.2f}\n'
            stats_text += f'Max: ${max_price:.2f}\n'
            stats_text += f'Avg: ${avg_price:.2f}'
            
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', 
                   facecolor='wheat', alpha=0.5), fontsize=9)
    
    def start(self):
        """Start the live viewer with auto-refresh."""
        ani = FuncAnimation(self.fig, self.update_plot, 
                          interval=self.update_interval, cache_frame_data=False)
        
        plt.suptitle('Live Token Price Monitor', fontsize=16, fontweight='bold', y=0.995)
        print(f"Live viewer started. Refreshing every {self.update_interval/1000:.1f} seconds.")
        print("Close the window to exit.")
        plt.show()


def main():
    """Main function to run the live viewer."""
    # Configure viewer parameters
    SYMBOLS = ['BTC', 'TAO']  # Symbols to display
    DATA_DIR = "data"
    UPDATE_INTERVAL = 5000  # milliseconds (5 seconds)
    
    viewer = LivePriceViewer(symbols=SYMBOLS, data_dir=DATA_DIR, 
                            update_interval=UPDATE_INTERVAL)
    viewer.start()


if __name__ == "__main__":
    main()

