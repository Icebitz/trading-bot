import matplotlib.pyplot as plt

def plot_strategy_results(df, portfolio_values):
  plt.figure(figsize=(12, 8))

  plt.subplot(2, 1, 1)
  plt.plot(df['close'], label="Close Price", alpha=0.5)
  plt.plot(df['ma_short'], label=f'MA{short_window}', alpha=0.8)
  plt.plot(df['ma_long'], label=f'MA{long_window}', alpha=0.8)

  buy_signals = df[df['signal'] == 'BUY']
  sell_signals = df[df['signal'] == 'SELL']
  plt.scatter(buy_signals.index, buy_signals['close'], 
              color='red', marker='^', label='BUY', s=100)
  plt.scatter(sell_signals.index, sell_signals['close'], 
              color='blue', marker='v', label='SELL', s=100)
  
  plt.subplot(2, 1, 2)
  plt.plot(portfolio_values, label='Portfolio Value', color='green')

  plt.legend()
  plt.savefig('charts/strategy_results.png')
  plt.show()