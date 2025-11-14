#!/usr/bin/env python3
"""Live signal monitor - checks signals in real time and logs BUY/SELL signals."""

import os
import sys
import time
import pandas as pd
from datetime import datetime

import requests
import dotenv
dotenv.load_dotenv()

# Make sure we can import from modules/
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.ma_strategy import MovingAverageStrategy

import matplotlib.pyplot as plt

def generate_signal_plot(df, filepath):
  df["timestamp"] = pd.to_datetime(df["timestamp"])

  now = df["timestamp"].iloc[-1]
  start = now - pd.Timedelta(days=1)
  df = df[df["timestamp"] >= start]

  if df.empty:
    return False

  plt.figure(figsize=(8, 4))

  plt.plot(df["timestamp"], df["price"], label="Price", linewidth=1)
  
  if "short_ma" in df:
    plt.plot(df["timestamp"], df["short_ma"], label="Short MA", linewidth=1)
  
  if "long_ma" in df:
    plt.plot(df["timestamp"], df["long_ma"], label="Long MA", linewidth=1)

  plt.title("BTC Price + Moving Averages (Last 24 hours)")
  plt.xlabel("Time")
  plt.ylabel("Price ($)")
  plt.legend()
  plt.grid(True, alpha=0.3, linestyle='--')

  plt.tight_layout()
  plt.savefig(filepath)
  plt.close()

  return True

def load_telegram_chat_ids():
  ids = os.getenv("TELEGRAM_CHAT_ID", "")
  if not ids:
    return []
  
  # Split by comma, trim whitespace
  return [chat_id.strip() for chat_id in ids.split(",") if chat_id.strip()]


def get_latest_signal(df):
  if df.empty or 'signal' not in df.columns:
    return None
  # Get the last non-NaN signal
  valid_signals = df[df['signal'].notna()]
  if valid_signals.empty:
    return None
  return valid_signals['signal'].iloc[-1]


def format_log_message(signal, row):
  timestamp = row['timestamp']
  price = row['price']
  
  if signal == 'HOLD': header_icon = '🔍'
  elif signal == 'BUY': header_icon = '🟢'
  elif signal == 'SELL': header_icon = '🔴'

  if pd.notna(row['short_ma']):
    short_ma_str = f"{row['short_ma']:.2f}"
  else:
    short_ma_str = 'N/A'
  
  if pd.notna(row['long_ma']):
    long_ma_str = f"{row['long_ma']:.2f}"
  else:
    long_ma_str = 'N/A'
  
  message = (
    f"{header_icon} {signal}\n"
    f"================================================\n"
    f"🕘 {timestamp}\n"
    f"💲 ${price:.2f}\n"
  )

  if signal != 'HOLD':
    message += f"🔍 {short_ma_str}\n"
    message += f"🔍 {long_ma_str}\n"

  return message


def send_telegram_message(message: str):
  TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

  chat_ids = load_telegram_chat_ids()
  for chat_id in chat_ids:
    payload = {
      'chat_id': chat_id,
      'text': message
    }
    requests.post(url, data=payload)


def send_telegram_plot(filepath):
  TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
  chat_ids = load_telegram_chat_ids()

  for chat_id in chat_ids:
    with open(filepath, 'rb') as photo:
      payload = { 'chat_id': chat_id }
      files = { 'photo': (filepath, photo) }
      requests.post(url, data=payload, files=files)

def main():
  csv_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_prices.csv')
  check_interval = 60  # Check every 60 seconds
  
  short_window = os.getenv('SHORT_WINDOW', 50)
  long_window = os.getenv('LONG_WINDOW', 200)
  strategy = MovingAverageStrategy(short_window=int(short_window), long_window=int(long_window))
  last_signal = None
  
  print("=" * 80)
  print("Live Signal Monitor Started")
  print(f"Monitoring: {csv_file}")
  print(f"Check interval: {check_interval} seconds")
  print("=" * 80)
  print()
  
  try:
    while True:
      # Check if file exists
      if not os.path.exists(csv_file):
        print(f"[{datetime.now()}] Waiting for data file: {csv_file}")
        time.sleep(check_interval)
        continue
      
      # Read and process data
      try:
        df = pd.read_csv(csv_file)
        
        if df.empty:
          print(f"[{datetime.now()}] No data in file yet...")
          time.sleep(check_interval)
          continue
        
        # Ensure timestamp is sorted
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate moving averages and generate signals
        df = strategy.calculate_moving_averages(df)
        df = strategy.generate_signals(df)
        
        # Get the latest signal
        current_signal = get_latest_signal(df)
        
        if current_signal is None:
          print(f"[{datetime.now()}] Waiting for enough data to calculate signals...")
          time.sleep(check_interval)
          continue
        
        # Check if signal changed to BUY or SELL
        if current_signal in ['BUY', 'SELL', 'HOLD']:
          # Get the latest row with signal
          valid_df = df[df['signal'].notna()]
          if not valid_df.empty:
            latest_row = valid_df.iloc[-1]
            
            # Only log if this is a new BUY/SELL signal (not the same as last)
            if current_signal != last_signal:
              log_message = format_log_message(current_signal, latest_row)
              print(f"*** {log_message} ***")

              send_telegram_message(log_message)

              plot_filepath = os.path.join(os.path.dirname(__file__), 'charts', 'signal_plot.png')
              if generate_signal_plot(df, plot_filepath):
                send_telegram_plot(plot_filepath)

              last_signal = current_signal

        else:
          # Reset last_signal if we're back to HOLD
          if last_signal in ['BUY', 'SELL']:
            last_signal = None
        
      except Exception as e:
        print(f"[{datetime.now()}] Error processing data: {e}")
      
      # Wait before next check
      time.sleep(check_interval)
      
  except KeyboardInterrupt:
    print()
    print("=" * 80)
    print("Live Signal Monitor Stopped")
    print("=" * 80)


if __name__ == '__main__':
  main()

