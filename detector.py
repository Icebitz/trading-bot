import pandas as pd

def find_pattern(df, jump_threshold=2.0):
    patterns = []
    
    # Calculate percentage change
    df = df.copy()
    df['change'] = df['price'].pct_change() * 100
    
    # 1. Find sharp rising patterns (above threshold)
    big_jumps = df[df['change'] > jump_threshold]
    if len(big_jumps) > 0:
        patterns.append(f"Sharp rises (>{jump_threshold}%): {len(big_jumps)} times")
        max_jump = df['change'].max()
        patterns.append(f"Max increase: {max_jump:.2f}%")
    
    # 2. Find sharp falling patterns
    big_drops = df[df['change'] < -jump_threshold]
    if len(big_drops) > 0:
        patterns.append(f"Sharp drops (<-{jump_threshold}%): {len(big_drops)} times")
        min_drop = df['change'].min()
        patterns.append(f"Max decrease: {min_drop:.2f}%")
    
    # 3. Volatility patterns by time period
    try:
        time_vols = [
            ['00:00', '03:00'],
            ['03:00', '06:00'],
            ['06:00', '09:00'],
            ['09:00', '12:00'],
            ['12:00', '15:00'],
            ['15:00', '18:00'],
            ['18:00', '21:00'],
            ['21:00', '23:59'],
        ]
        for vol in time_vols:
            period_vol = df.between_time(vol[0], vol[1])['change'].std()
            patterns.append(f"Volatility ({vol[0]} - {vol[1]}): {period_vol:.2f}%")

    except:
        # If time filtering fails, calculate overall volatility
        overall_vol = df['change'].std()
        patterns.append(f"Overall volatility: {overall_vol:.2f}%")
    
    # 4. Price trend
    price_change = ((df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0]) * 100
    patterns.append(f"Total price change: {price_change:.2f}%")
    
    return patterns


# Example usage
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
        print("Usage: python3 detector.py [csv_file] [jump_threshold]")
        print("Examples:")
        print("  python3 detector.py                    # Use default data/btc_prices.csv")
        print("  python3 detector.py test_data.csv      # Use test_data.csv")
        print("  python3 detector.py test_data.csv 1.5   # Use test_data.csv with 1.5% threshold")
        sys.exit(1)
    
    # Get jump threshold from command line
    jump_threshold = 2.0
    if len(sys.argv) > 2:
        try:
            jump_threshold = float(sys.argv[2])
        except ValueError:
            print(f"Warning: Invalid threshold '{sys.argv[2]}', using default 2.0%")
    
    print(f"Analyzing: {csv_file}")
    print(f"Jump threshold: {jump_threshold}%")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv(csv_file)
    
    # Handle different timestamp formats robustly
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    except:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        except:
            df['timestamp'] = pd.to_datetime(df['timestamp'], infer_datetime_format=True)
    
    df = df.set_index('timestamp')
    
    # Find patterns
    patterns = find_pattern(df, jump_threshold=jump_threshold)
    
    # Get base name for display
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    print(f"=== {base_name.upper()} Price Patterns ===")
    for pattern in patterns:
        print(f"  • {pattern}")

