#!/usr/bin/env python3
"""Test script for pattern detection"""

import pandas as pd
from detect import find_pattern

def test_find_pattern():
    """Test the find_pattern function with different thresholds"""
    
    # Load data
    print("Loading BTC price data...")
    df = pd.read_csv('data/btc_prices.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    
    print(f"Loaded {len(df)} records")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}\n")
    
    # Test with different thresholds
    thresholds = [0.5, 1.0, 2.0, 5.0]
    
    for threshold in thresholds:
        print(f"\n{'='*50}")
        print(f"Testing with {threshold}% threshold")
        print('='*50)
        
        patterns = find_pattern(df, jump_threshold=threshold)
        
        for pattern in patterns:
            print(f"  • {pattern}")

if __name__ == "__main__":
    test_find_pattern()

