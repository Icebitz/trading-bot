import pandas as pd
import matplotlib.pyplot as plt
import os

class Analyzer:
    def load_and_plot(self, csv_file='../data/btc_prices.csv', output_image='../charts/price_chart.png', title='Price History'):
        df = pd.read_csv(csv_file)
        
        # Convert timestamp column
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        elif 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')

        # Get last 24 hours of data
        df = df.tail(24 * 60)

        # Create chart
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['price'], label='Price', linewidth=1)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        os.makedirs(os.path.dirname(output_image), exist_ok=True)
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        print(f"Chart saved: {output_image}")
        
        # Show chart
        plt.show()
        
        return df


if __name__ == "__main__":
    import sys
    
    # Only two options: no arg (default file) or CSV path
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        csv_file = sys.argv[1]
    else:
        csv_file = '../data/btc_prices.csv'
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found!")
        print("Usage: python3 analyzer.py [csv_file]")
        print("Examples:")
        print("  python3 analyzer.py                    # Use default ../data/btc_prices.csv")
        print("  python3 analyzer.py test_data.csv      # Use test_data.csv")
        sys.exit(1)
    
    analyzer = Analyzer()
    
    # Generate output filename based on input
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    output_image = f'../charts/{base_name}_chart.png'
    
    print(f"Analyzing: {csv_file}")
    print(f"Output: {output_image}")
    
    # Generate chart
    df = analyzer.load_and_plot(
        csv_file=csv_file, 
        output_image=output_image, 
        title=f'{base_name.title()} Price Trend'
    )

