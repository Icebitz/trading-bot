class Backtester:
  def __init__(self, initial_capital=1000000):
    self.initial_capital = initial_capital
    self.position = 0
    self.cash = initial_capital
    self.portfolio_value = []
  
  def run_backtest(self, df):
    for _, row in df.iterrows():
      if row['signal'] == 'BUY' and self.position == 0:
        self.position = 1
        self.cash -= row['price']
      elif row['signal'] == 'SELL' and self.position == 1:
        self.position = 0
        self.cash += row['price']
      
      current_value = self.cash + self.position * row['price']
      self.portfolio_value.append(current_value)

    return self.calculate_performance(df)
  
  def calculate_performance(self, df):
    final_value = self.portfolio_value[-1]
    total_return = (final_value - self.initial_capital) / self.initial_capital * 100

    return {
      'total_return': total_return,
      'final_value': final_value,
      'max_drawdown': self.calculate_max_drawdown(),
      'win_rate': self.calculate_win_rate(df)
    }
  
  def calculate_max_drawdown(self):
    max_drawdown = 0.0
    peak = self.portfolio_value[0]
    for value in self.portfolio_value:
      if value > peak:
        peak = value
      drawdown = (peak - value) / peak
      if drawdown > max_drawdown:
        max_drawdown = drawdown
    return max_drawdown
  
  def calculate_win_rate(self, df):
    wins = 0
    total = len(df)
    for i in range(1, len(df)):
      if df['signal'].iloc[i] == 'BUY' and df['signal'].iloc[i-1] == 'SELL':
        wins += 1
    return wins / total