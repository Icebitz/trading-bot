import pandas as pd
import matplotlib.pyplot as plt
import pytz
from datetime import datetime, timedelta

class Analyzer:
    def load_and_plot(self, csv_file='data/btc_prices.csv', output_image='charts/price_chart.png', title='Price History'):
        # Load CSV data
        df = pd.read_csv(csv_file)
        
        # Convert timestamp column to datetime type
        if 'timestamp' in df.columns:
            # Try different parsing methods for robust timestamp handling
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            except:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
                except:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], infer_datetime_format=True)
            df = df.set_index('timestamp')
        elif 'datetime' in df.columns:
            try:
                df['datetime'] = pd.to_datetime(df['datetime'], format='ISO8601')
            except:
                try:
                    df['datetime'] = pd.to_datetime(df['datetime'], format='mixed')
                except:
                    df['datetime'] = pd.to_datetime(df['datetime'], infer_datetime_format=True)
            df = df.set_index('datetime')
        
        # jst = pytz.timezone('Asia/Tokyo')
        # start_date = datetime.now(jst)
        # end_date = datetime.now(jst) + timedelta(minutes=10)

        # df = df[start_date:end_date]

        # LAST 10 minutes
        df = df.tail(100)

        # Create chart
        plt.figure(figsize=(12, 6))
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
    import sys
    import os
    
    # Get command line arguments
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = 'data/btc_prices.csv'
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found!")
        print("Usage: python3 analyzer.py [csv_file]")
        print("Examples:")
        print("  python3 analyzer.py                    # Use default data/btc_prices.csv")
        print("  python3 analyzer.py test_data.csv      # Use test_data.csv")
        sys.exit(1)
    
    analyzer = Analyzer()
    
    # Generate output filename based on input
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_image = f'charts/{base_name}_chart.png'
    
    print(f"Analyzing: {csv_file}")
    print(f"Output chart: {output_image}")
    
    # Create charts directory if it doesn't exist
    os.makedirs('charts', exist_ok=True)
    
    # Generate chart
    df = analyzer.load_and_plot(
        csv_file=csv_file, 
        output_image=output_image, 
        title=f'{base_name.title()} Price Trend'
    )

