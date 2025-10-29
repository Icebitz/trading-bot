import pandas as pd
import numpy as np

class MovingAverageStrategy:
  def __init__(self, short_window=50, long_window=200):
    self.short_window = short_window
    self.long_window = long_window

  def calculate_moving_averages(self, df):
    df['short_ma'] = df['price'].rolling(window=self.short_window).mean()
    df['long_ma'] = df['price'].rolling(window=self.long_window).mean()
    return df

  def generate_signals(self, df):
    signals = []
    for i in range(len(df)):
      current_short = df['short_ma'].iloc[i]
      current_long = df['long_ma'].iloc[i]
      previous_short = df['short_ma'].iloc[i-1]
      previous_long = df['long_ma'].iloc[i-1]
      if previous_short < previous_long and current_short > current_long:
        signals.append('BUY')
      elif previous_short > previous_long and current_short < current_long:
        signals.append('SELL')
      else:
        signals.append('HOLD')
    df['signal'] = signals
    return df
