import pandas as pd
import matplotlib.pyplot as plt

class Analyzer:
    def load_and_plot(self, csv_file='data/btc_prices.csv', output_image='charts/price_chart.png', title='Price History'):
        """Load data from CSV and draw price chart"""
        # Load CSV data
        df = pd.read_csv(csv_file)
        
        # Convert datetime column to datetime type
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
        elif 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.set_index('timestamp')
        
        # Create chart
        plt.figure(figsize=(18, 6))
        plt.plot(df.index, df['price'], label='Price', linewidth=1)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save before showing
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {output_image}")
        
        # Show chart
        plt.show()
        
        return df


# Run
if __name__ == "__main__":
    analyzer = Analyzer()
    df = analyzer.load_and_plot(title='Bitcoin Price Trend')

