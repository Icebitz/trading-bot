# Trading Bot - Setup Guide

Complete setup instructions for the BTC Price Trading Bot project.

---

## Prerequisites

Before starting, ensure you have:
- **Python 3.8+** installed (tested with Python 3.13)
- **pip** (Python package manager)
- **Internet connection** (for fetching BTC prices from Binance API)
- **Linux/Mac/Windows** OS supported

---

## Quick Start

### 1. Clone or Navigate to Project
```bash
cd /home/ubuntu/work/trading-bot
```

### 2. Create Virtual Environment (if not exists)
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
trading-bot/
├── recorder.py          # Records BTC prices from Binance API
├── analyzer.py          # Visualizes price history with charts
├── detector.py          # Detects patterns in price data
├── test_detect.py       # Test script for pattern detection
├── requirements.txt     # Python dependencies
├── observations.md      # Pattern discovery log
├── setup.md             # This file
├── README.md            # Project overview
├── .gitignore           # Git ignore rules
│
├── data/                # Price data storage
│   ├── .gitkeep         # Keeps directory in git
│   └── btc_prices.csv   # (ignored by git)
│
├── charts/              # Generated chart images
│   ├── .gitkeep         # Keeps directory in git
│   └── price_chart.png  # (ignored by git)
│
└── venv/                # Virtual environment (ignored by git)
```

---

## Dependencies

The project requires the following Python packages (see `requirements.txt`):

```
requests>=2.31.0      # API calls to Binance
pandas>=2.0.0         # Data analysis and manipulation
matplotlib>=3.7.0     # Chart visualization
schedule>=1.2.0       # Scheduled price recording
```

---

## Usage Guide

### 1. Recording BTC Prices

The `Recorder` class fetches live BTC prices from Binance API and saves them to CSV.

**Basic Usage:**
```bash
source venv/bin/activate
python recorder.py
```

**Quiet Mode (Minimal Logging):**
```bash
python recorder.py --quiet
```

**Check Mode (One-time Analysis):**
```bash
python recorder.py --check
```

**Customized Recording:**
```python
from recorder import Recorder

# Record every 30 seconds to data directory
recorder = Recorder(
    symbol='BTCUSDT',
    interval=30,
    filename='data/btc_prices.csv'  # Saves to data/ directory
)
recorder.start()
```

**Options:**
- `symbol`: Trading pair (default: 'BTCUSDT')
- `interval`: Recording interval in seconds (default: 60)
- `filename`: Output CSV file (default: 'data/btc_prices.csv')
- `verbose`: Enable detailed logging (default: True)

**Stop Recording:** Press `Ctrl+C`

---

### 2. Analyzing & Visualizing Prices

The `Analyzer` class creates price trend charts from CSV data.

**Basic Usage:**
```bash
source venv/bin/activate
python analyzer.py
```

**Custom Analysis:**
```python
from analyzer import Analyzer

analyzer = Analyzer()

# Analyze BTC prices
df = analyzer.load_and_plot(
    csv_file='data/btc_prices.csv',
    output_image='charts/btc_chart.png',
    title='Bitcoin Price Trend'
)

# Analyze other cryptocurrencies
df = analyzer.load_and_plot(
    csv_file='data/tao_price_history.csv',
    output_image='charts/tao_chart.png',
    title='TAO Price History'
)
```

**Output:**
- Chart saved as PNG image
- Returns DataFrame for further analysis
- Displays interactive chart window

---

### 3. Pattern Detection

The `find_pattern` function identifies trading patterns in price data.

**Basic Usage:**
```bash
source venv/bin/activate
python detector.py
```

**Output Example:**
```
=== BTC Price Patterns ===
  • Sharp rises (>2%): 3 times
  • Max increase: 2.45%
  • Morning volatility (6-12): 0.07%
  • Afternoon volatility (12-18): 0.04%
  • Evening volatility (18-24): 0.03%
  • Total price change: 1.96%
```

**Custom Pattern Detection:**
```python
from detector import find_pattern
import pandas as pd

# Load data
df = pd.read_csv('data/btc_prices.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp')

# Detect patterns with custom threshold
patterns = find_pattern(df, jump_threshold=1.0)  # More sensitive

# Print results
for pattern in patterns:
    print(pattern)
```

**Pattern Types Detected:**
- Sharp price rises/drops
- Volatility by time period
- Overall price trends
- Max increase/decrease events

---

### 4. Testing Pattern Detection

Run the test suite:
```bash
source venv/bin/activate
python test_detect.py
```

---

## Workflows

### Complete Analysis Workflow

1. **Start Recording** (run in background)
   ```bash
   source venv/bin/activate
   python recorder.py &
   ```

2. **Analyze Data** (after collecting data)
   ```bash
   python analyzer.py
   ```

3. **Detect Patterns**
   ```bash
   python detector.py
   ```

4. **Document Findings**
   - Update `observations.md` with discoveries
   - Save generated charts to `charts/` directory

---

## Configuration

### Change Data Source

Edit `recorder.py` to use different API:
```python
# Use MEXC instead of Binance
self.api_url = 'https://api.mexc.com/api/v3/ticker/price'
```

### Adjust Recording Interval

```python
recorder = Recorder(symbol='BTCUSDT', interval=300)  # Every 5 minutes
```

### Customize Pattern Thresholds

```python
patterns = find_pattern(df, jump_threshold=5.0)  # Only detect >5% changes
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pandas'`
**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Virtual environment not activating
**Solution (Linux/Mac):**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### Issue: API connection fails
**Solution:**
- Check internet connection
- Verify Binance API is accessible: `curl https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT`
- Try alternative API endpoint in `recorder.py`

### Issue: Charts not displaying
**Solution:**
- Ensure X11 forwarding if using SSH: `ssh -X user@host`
- Charts are saved as PNG even if display fails
- Use headless mode by commenting out `plt.show()` in `analyzer.py`

### Issue: Permission denied on CSV files
**Solution:**
```bash
chmod 644 data/*.csv
```

---

## Best Practices

1. **Always activate virtual environment** before running scripts
2. **Run recorder in background** or separate terminal for continuous data collection
3. **Backup CSV files** regularly to prevent data loss
4. **Document patterns** in `observations.md` after analysis
5. **Use version control** (git) but exclude `venv/` and `__pycache__/`

---

## Development

### Adding New Features

1. Create feature branch
2. Add tests in `test_*.py`
3. Update documentation
4. Test with real data

### Extending Pattern Detection

Add new patterns in `detector.py`:
```python
def find_pattern(df, jump_threshold=2.0):
    patterns = []
    
    # Your custom pattern logic here
    # Example: Detect consecutive rises
    consecutive_rises = 0
    for change in df['change']:
        if change > 0:
            consecutive_rises += 1
        else:
            consecutive_rises = 0
    
    patterns.append(f"Max consecutive rises: {consecutive_rises}")
    return patterns
```

---

## Resources

- **Binance API Docs**: https://binance-docs.github.io/apidocs/spot/en/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **Matplotlib Docs**: https://matplotlib.org/stable/contents.html

---

## Support & Contribution

For issues, improvements, or questions:
1. Check `observations.md` for pattern insights
2. Review this setup guide
3. Test with `test_detect.py`

---

## License

This is a personal trading analysis tool. Use at your own risk.

**Disclaimer**: This tool is for educational purposes. Not financial advice.

---

*Last Updated: October 19, 2025*

