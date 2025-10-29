#!/usr/bin/env python3
"""
Test suite for the Backtester module.
Tests backtesting functionality with real MA strategy data.
"""

import unittest
import os
import sys
import pandas as pd
import numpy as np

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from backtester import Backtester


class TestBacktester(unittest.TestCase):
    """Test cases for the Backtester class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.backtester = Backtester(initial_capital=100000)
    
    def test_initialization(self):
        """Test Backtester initialization."""
        self.assertEqual(self.backtester.initial_capital, 100000)
        self.assertEqual(self.backtester.position, 0)
        self.assertEqual(self.backtester.cash, 100000)
        self.assertEqual(len(self.backtester.portfolio_value), 0)
    
    def test_buy_signal_execution(self):
        """Test that BUY signals are executed correctly."""
        # Create test data with BUY signal
        test_data = pd.DataFrame({
            'price': [100, 101, 102],
            'signal': ['HOLD', 'BUY', 'HOLD']
        })
        
        self.backtester.run_backtest(test_data)
        
        # Should have bought at price 101
        self.assertEqual(self.backtester.position, 1)
        self.assertEqual(self.backtester.cash, 100000 - 101)
    
    def test_sell_signal_execution(self):
        """Test that SELL signals are executed correctly."""
        # Create test data with BUY then SELL
        test_data = pd.DataFrame({
            'price': [100, 101, 102, 103],
            'signal': ['HOLD', 'BUY', 'HOLD', 'SELL']
        })
        
        self.backtester.run_backtest(test_data)
        
        # Should have sold at price 103
        self.assertEqual(self.backtester.position, 0)
        self.assertEqual(self.backtester.cash, 100000 - 101 + 103)
    
    def test_portfolio_value_calculation(self):
        """Test portfolio value calculation."""
        test_data = pd.DataFrame({
            'price': [100, 101, 102],
            'signal': ['HOLD', 'BUY', 'HOLD']
        })
        
        self.backtester.run_backtest(test_data)
        
        # Portfolio value should be calculated for each row
        self.assertEqual(len(self.backtester.portfolio_value), 3)
        
        # First value should be initial capital (no position)
        self.assertEqual(self.backtester.portfolio_value[0], 100000)
        
        # Second value should be cash + position * price (after BUY)
        expected_value = (100000 - 101) + (1 * 101)
        self.assertEqual(self.backtester.portfolio_value[1], expected_value)
    
    def test_performance_calculation(self):
        """Test performance metrics calculation."""
        # Create profitable test data
        test_data = pd.DataFrame({
            'price': [100, 95, 105, 110],
            'signal': ['HOLD', 'BUY', 'HOLD', 'SELL']
        })
        
        performance = self.backtester.run_backtest(test_data)
        
        # Should have positive return (bought at 95, sold at 110)
        self.assertGreater(performance['total_return'], 0)
        self.assertGreater(performance['final_value'], self.backtester.initial_capital)
        self.assertIsInstance(performance['max_drawdown'], float)
        self.assertIsInstance(performance['win_rate'], float)
    
    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation."""
        # Create data with a drawdown
        test_data = pd.DataFrame({
            'price': [100, 95, 90, 85, 90, 95, 100],
            'signal': ['HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'SELL']
        })
        
        self.backtester.run_backtest(test_data)
        max_drawdown = self.backtester.calculate_max_drawdown()
        
        # Max drawdown should be between 0 and 1
        self.assertGreaterEqual(max_drawdown, 0)
        self.assertLessEqual(max_drawdown, 1)
    
    def test_win_rate_calculation(self):
        """Test win rate calculation."""
        # Create data with known win/loss pattern
        test_data = pd.DataFrame({
            'price': [100, 95, 105, 100, 90, 95],
            'signal': ['HOLD', 'BUY', 'SELL', 'BUY', 'SELL', 'HOLD']
        })
        
        self.backtester.run_backtest(test_data)
        win_rate = self.backtester.calculate_win_rate(test_data)
        
        # Win rate should be between 0 and 1
        self.assertGreaterEqual(win_rate, 0)
        self.assertLessEqual(win_rate, 1)


class TestBacktesterWithRealData(unittest.TestCase):
    """Test Backtester with real MA strategy data."""
    
    def setUp(self):
        """Set up test with real data."""
        self.backtester = Backtester(initial_capital=1000000)
        
        # Load real MA strategy data
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_ma_signals.csv')
        if not os.path.exists(data_file):
            self.skipTest(f"Real data file not found: {data_file}")
        
        self.df = pd.read_csv(data_file)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        # Filter out rows with NaN signals (first 200 rows due to MA calculation)
        self.df = self.df.dropna(subset=['signal'])
    
    def test_real_data_backtest(self):
        """Test backtesting with real BTC MA strategy data."""
        print(f"\n=== Testing with Real Data ===")
        print(f"Data points: {len(self.df)}")
        print(f"Date range: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}")
        
        # Count signals
        signal_counts = self.df['signal'].value_counts()
        print(f"Signal distribution:")
        for signal, count in signal_counts.items():
            print(f"  {signal}: {count}")
        
        # Run backtest
        performance = self.backtester.run_backtest(self.df)
        
        # Display results
        print(f"\n=== Backtest Results ===")
        print(f"Initial capital: ${self.backtester.initial_capital:,.2f}")
        print(f"Final value: ${performance['final_value']:,.2f}")
        print(f"Total return: {performance['total_return']:.2f}%")
        print(f"Max drawdown: {performance['max_drawdown']:.2f}%")
        print(f"Win rate: {performance['win_rate']:.6f}%")
        
        # Basic assertions
        self.assertIsInstance(performance['total_return'], float)
        self.assertIsInstance(performance['final_value'], float)
        self.assertIsInstance(performance['max_drawdown'], float)
        self.assertIsInstance(performance['win_rate'], float)
        
        # Portfolio value should be calculated for each data point
        self.assertEqual(len(self.backtester.portfolio_value), len(self.df))
        
        print(f"\n=== Portfolio Value Analysis ===")
        portfolio_values = np.array(self.backtester.portfolio_value)
        print(f"Min portfolio value: ${portfolio_values.min():,.2f}")
        print(f"Max portfolio value: ${portfolio_values.max():,.2f}")
        print(f"Final portfolio value: ${portfolio_values[-1]:,.2f}")
        
        # Save results to CSV with formatted numbers
        results_df = self.df.copy()
        results_df['portfolio_value'] = self.backtester.portfolio_value
        results_df['daily_return'] = results_df['portfolio_value'].pct_change() * 100
        
        # Format numbers to 2 decimal places
        results_df['price'] = results_df['price'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "")
        results_df['short_ma'] = results_df['short_ma'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "")
        results_df['long_ma'] = results_df['long_ma'].apply(lambda x: f"{x:.2f}" if not pd.isna(x) else "")
        results_df['portfolio_value'] = results_df['portfolio_value'].apply(lambda x: f"{x:.2f}")
        results_df['daily_return'] = results_df['daily_return'].apply(lambda x: f"{x:.6f}" if not pd.isna(x) else "")
        
        output_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_backtest_results.csv')
        results_df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
        print(f"Total rows saved: {len(results_df)}")


if __name__ == '__main__':
    print("Running Backtester Tests...")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("Backtester tests completed!")
