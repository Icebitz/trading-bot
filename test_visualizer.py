#!/usr/bin/env python3
"""Test script for visualizer.py - generates strategy visualization charts."""

import os
import sys
import pandas as pd

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.visualizer import plot_strategy_results


def main():
  # Check if backtest results exist, otherwise use MA signals
  backtest_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_backtest.csv')
  
  if os.path.exists(backtest_file):
    print(f"Using backtest results: {backtest_file}")
    df = pd.read_csv(backtest_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
  
  # Check if we have price data
  if 'price' not in df.columns and 'close' not in df.columns:
    print("Error: No 'price' or 'close' column found in data.")
    return
  
  print(f"\nGenerating visualization...")
  print(f"Data points: {len(df)}")
  
  # Ensure charts directory exists
  os.makedirs('charts', exist_ok=True)
  
  # Generate visualization
  output_image = "charts/strategy_results.png"
  plot_strategy_results(df, output_image)
  
  print(f"\nChart saved to: {output_image}")


if __name__ == '__main__':
  main()

