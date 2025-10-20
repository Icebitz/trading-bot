import pandas as pd

def find_pattern(df, jump_threshold=2.0):
    """Find specific patterns in BTC price data
    
    Args:
        df: DataFrame with price data (indexed by datetime)
        jump_threshold: Percentage threshold for detecting sharp price changes (default: 2.0%)
    
    Returns:
        list: Detected patterns
    """
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
        morning_vol = df.between_time('06:00', '12:00')['change'].std()
        afternoon_vol = df.between_time('12:00', '18:00')['change'].std()
        evening_vol = df.between_time('18:00', '23:59')['change'].std()
        
        patterns.append(f"Morning volatility (6-12): {morning_vol:.2f}%")
        patterns.append(f"Afternoon volatility (12-18): {afternoon_vol:.2f}%")
        patterns.append(f"Evening volatility (18-24): {evening_vol:.2f}%")
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
    # Load data
    df = pd.read_csv('data/btc_prices.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    
    # Find patterns
    patterns = find_pattern(df, jump_threshold=2.0)
    
    print("=== BTC Price Patterns ===")
    for pattern in patterns:
        print(f"  • {pattern}")

