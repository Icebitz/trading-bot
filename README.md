# Real-Time Token Price Recorder

A Python application for recording cryptocurrency token prices in real-time and visualizing the data.

## Features

- **Real-time Price Recording**: Continuously fetches and saves token prices to CSV files
- **Data Storage**: Organized CSV storage with timestamps for historical analysis
- **Static Visualization**: View historical price data with statistics
- **Live Visualization**: Auto-refreshing charts that update as new data is recorded
- **Multi-token Support**: Track multiple tokens simultaneously (BTC, TAO, etc.)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Binance API credentials (optional for public data):
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

## Usage

### 1. Record Token Prices

Start recording prices in real-time:

```bash
python price_recorder.py
```

This will:
- Create a `data/` directory
- Fetch prices every 5 seconds (configurable)
- Save data to CSV files: `btc_price_history.csv`, `tao_price_history.csv`
- Display prices in the console
- Press `Ctrl+C` to stop recording

### 2. View Price Data (Static)

View historical price data with graphs:

```bash
python price_viewer.py
```

This will display:
- Statistics for each token
- Comparative graphs (normalized to percentage change)

You can customize the viewer by editing the `main()` function:

```python
# View single token
viewer.plot_single_token('BTC')

# View last 100 records only
viewer.plot_single_token('BTC', tail=100)

# Compare multiple tokens (absolute prices)
viewer.plot_multiple_tokens(['BTC', 'TAO'])

# Compare multiple tokens (normalized percentage change)
viewer.plot_multiple_tokens(['BTC', 'TAO'], normalize=True)

# Get statistics
viewer.get_statistics('BTC')
```

### 3. Live Price Viewer

View prices with auto-refreshing charts:

```bash
python price_viewer_live.py
```

This will:
- Open a window with live-updating charts
- Refresh every 5 seconds
- Show the last 100 data points per token
- Display current price, min, max, and average

**Tip**: Run `price_recorder.py` in one terminal and `price_viewer_live.py` in another to see real-time updates!

## Configuration

### Recording Interval

Edit `price_recorder.py`:

```python
INTERVAL = 5  # seconds between recordings
```

### Update Interval (Live Viewer)

Edit `price_viewer_live.py`:

```python
UPDATE_INTERVAL = 5000  # milliseconds (5 seconds)
```

### Add More Tokens

1. Add a price function in `config.py`:
```python
def get_eth_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
    response = requests.get(url).json()
    return response["price"]
```

2. Update `price_recorder.py`:
```python
SYMBOLS = ['BTC', 'TAO', 'ETH']

# Add to price_functions dictionary
self.price_functions = {
    'BTC': get_btc_price,
    'TAO': get_tao_price,
    'ETH': get_eth_price
}
```

## Data Format

CSV files contain the following columns:
- `timestamp`: Unix timestamp
- `datetime`: Human-readable date and time
- `symbol`: Token symbol (BTC, TAO, etc.)
- `price`: Token price in USD

Example:
```csv
timestamp,datetime,symbol,price
1729123456.78,2024-10-16 14:30:56,BTC,67234.56
```

## Project Structure

```
pro/
├── config.py                 # API configuration and price functions
├── price_recorder.py         # Real-time price recording script
├── price_viewer.py          # Static data visualization
├── price_viewer_live.py     # Live data visualization
├── requirements.txt         # Python dependencies
├── data/                    # CSV data storage (created automatically)
│   ├── btc_price_history.csv
│   └── tao_price_history.csv
└── README.md
```

## Tips

- **Long-term Recording**: Use `nohup` or `screen` to keep the recorder running:
  ```bash
  nohup python price_recorder.py &
  ```

- **Data Analysis**: Import CSV files into pandas for custom analysis:
  ```python
  import pandas as pd
  df = pd.read_csv('data/btc_price_history.csv')
  ```

- **Performance**: Adjust recording interval based on your needs. Shorter intervals = more data but higher API usage.

## Troubleshooting

- **No module found**: Run `pip install -r requirements.txt`
- **API errors**: Check your internet connection and Binance API status
- **No data directory**: The recorder creates it automatically on first run
- **Empty graphs**: Make sure the recorder has been running for at least a few minutes

