#!/usr/bin/env python3
"""Simple test for Moving Average Strategy using real price history."""

import os
import sys
import unittest
import pandas as pd

# Make sure we can import from modules/
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from ma_strategy import MovingAverageStrategy


class TestMAStrategyWithRealData(unittest.TestCase):
  def test_real_data_ma_signals(self):
    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_prices.csv')
    self.assertTrue(os.path.exists(csv_file), f"Missing data file: {csv_file}")

    df = pd.read_csv(csv_file)
    self.assertIn('timestamp', df.columns)
    self.assertIn('price', df.columns)

    # Ensure timestamp is sorted
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Compute MAs and signals (50/200 are common defaults)
    strategy = MovingAverageStrategy(short_window=50, long_window=200)
    df = strategy.calculate_moving_averages(df)
    df = strategy.generate_signals(df)

    # Basic assertions - simple and robust
    self.assertIn('short_ma', df.columns)
    self.assertIn('long_ma', df.columns)
    self.assertIn('signal', df.columns)

    # At least some rows should have non-NaN MAs
    valid = df.dropna(subset=['short_ma', 'long_ma'])
    self.assertGreater(len(valid), 0, 'Not enough rows to compute moving averages')

    # Signals should be one of the allowed values
    allowed = {'BUY', 'SELL', 'HOLD'}
    self.assertTrue(set(df['signal'].unique()).issubset(allowed))

    # Print signal arrays for better visibility
    print('\nSignal summary from real data:')
    counts = df['signal'].value_counts()
    for s, c in counts.items():
      print(f"  {s}: {c}")
    
    # Display signal arrays
    print('\nSignal arrays:')
    hold_indices = df[df['signal'] == 'HOLD'].index.tolist()
    sell_indices = df[df['signal'] == 'SELL'].index.tolist()
    buy_indices = df[df['signal'] == 'BUY'].index.tolist()
    
    print(f"HOLD indices: {hold_indices[:10]}{'...' if len(hold_indices) > 10 else ''} (total: {len(hold_indices)})")
    print(f"SELL indices: {sell_indices}")
    print(f"BUY indices: {buy_indices}")
    
    # Show some example signals with timestamps and prices
    print('\nExample signals (first 10):')
    example_df = df[['timestamp', 'price', 'short_ma', 'long_ma', 'signal']].head(10)
    for idx, row in example_df.iterrows():
      timestamp = row['timestamp']
      price = row['price']
      signal = row['signal']
      short_ma_str = f"{row['short_ma']:.2f}" if not pd.isna(row['short_ma']) else 'N/A'
      long_ma_str = f"{row['long_ma']:.2f}" if not pd.isna(row['long_ma']) else 'N/A'
      print(f"  {timestamp}: ${price:.2f} | Short MA: {short_ma_str} | Long MA: {long_ma_str} | Signal: {signal}")
    
    # Save results to CSV file with formatted numbers
    output_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_ma_signals.csv')
    
    # Format moving averages to 2 decimal places
    df_formatted = df.copy()
    df_formatted['short_ma'] = df_formatted['short_ma'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "")
    df_formatted['long_ma'] = df_formatted['long_ma'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "")
    
    df_formatted.to_csv(output_file, index=False)
    print(f'\nResults saved to: {output_file}')
    print(f'Total rows saved: {len(df)}')


if __name__ == '__main__':
  unittest.main(verbosity=2)
