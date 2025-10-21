#!/usr/bin/env python3
"""Test script for pattern detection"""

import pandas as pd
from detector import find_pattern

def test_find_pattern():
    """Test the find_pattern function with different thresholds"""
    
    # Load data
    print("Loading BTC price data...")
    df = pd.read_csv('data/btc_prices.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    
    print(f"Loaded {len(df)} records")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}\n")
    
    # Test with different thresholds
    thresholds = [0.1, 1]
    
    for threshold in thresholds:
        print(f"\n{'='*50}")
        print(f"Testing with {threshold}% threshold")
        print('='*50)
        
        patterns = find_pattern(df, jump_threshold=threshold)
        
        for pattern in patterns:
            print(f"  • {pattern}")
    
    print("\n")

if __name__ == "__main__":
    test_find_pattern()

