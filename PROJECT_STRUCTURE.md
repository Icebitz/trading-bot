# Project Structure Documentation

## ✅ Current Structure (Corrected)

```
trading-bot/
├── .git/                   # Git repository
├── .gitignore              # Git ignore rules (updated)
│
├── README.md               # Project overview & quick start
├── setup.md                # Detailed setup instructions
├── observations.md         # Pattern discovery log
│
├── recorder.py             # Price recording module
├── analyzer.py             # Chart visualization module
├── detect.py               # Pattern detection module
├── test_detect.py          # Test suite
├── requirements.txt        # Python dependencies
│
├── data/                   # Price data storage
│   ├── .gitkeep            # Keep directory in git
│   └── btc_prices.csv      # BTC price data (git ignored)
│
├── charts/                 # Generated chart images
│   ├── .gitkeep            # Keep directory in git
│   └── price_chart.png     # Generated charts (git ignored)
│
├── __pycache__/            # Python cache (git ignored)
└── venv/                   # Virtual environment (git ignored)
```

---

## 🔧 Changes Made

### 1. **Standardized Directory Names**
- ❌ Old: Mixed use of `chart/` (singular) in code
- ✅ New: Consistent use of `charts/` (plural) throughout

### 2. **Fixed Recorder Default Path**
- ❌ Old: `filename='btc_price_data.csv'` (saves to root)
- ✅ New: `filename='data/btc_prices.csv'` (saves to data/ directory)

### 3. **Fixed Analyzer Default Path**
- ❌ Old: `output_image='chart/price_chart.png'`
- ✅ New: `output_image='charts/price_chart.png'`

### 4. **Enhanced .gitignore**
```diff
+ # Python
  venv/
+ __pycache__/
+ *.pyc
+ *.pyo
+ *.pyd
+ .Python
+
+ # Environment
  .env
+ .venv
+
+ # Data files
+ data/*.csv
+ !data/.gitkeep
+
+ # Generated charts
+ charts/*.png
+ !charts/.gitkeep
+
+ # IDE
+ .vscode/
+ .idea/
+ *.swp
+ *.swo
+ *~
+
+ # OS
+ .DS_Store
+ Thumbs.db
+
+ # Logs
+ *.log
```

### 5. **Added .gitkeep Files**
- ✅ `data/.gitkeep` - Ensures data/ directory is tracked
- ✅ `charts/.gitkeep` - Ensures charts/ directory is tracked

### 6. **Updated All Documentation**
- ✅ `README.md` - Updated structure and code examples
- ✅ `setup.md` - Updated structure and path references
- ✅ Consistent paths across all documentation

---

## 📝 File Purposes

### Core Modules

| File | Purpose | Default Behavior |
|------|---------|-----------------|
| `recorder.py` | Fetches BTC prices from Binance API | Saves to `data/btc_prices.csv` |
| `analyzer.py` | Creates price trend charts | Saves to `charts/price_chart.png` |
| `detect.py` | Detects price patterns | Prints patterns to console |
| `test_detect.py` | Tests pattern detection | Runs test suite |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `.gitignore` | Specifies files to ignore in git |
| `venv/` | Isolated Python environment |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start, examples |
| `setup.md` | Detailed setup & troubleshooting guide |
| `observations.md` | Log of pattern discoveries |
| `PROJECT_STRUCTURE.md` | This file - structure documentation |

### Data Directories

| Directory | Purpose | Git Behavior |
|-----------|---------|--------------|
| `data/` | Stores CSV price data | Directory tracked, `.csv` files ignored |
| `charts/` | Stores generated PNG charts | Directory tracked, `.png` files ignored |

---

## 🎯 Design Principles

### 1. **Separation of Concerns**
- **Data** - Stored in `data/` directory
- **Output** - Charts saved in `charts/` directory
- **Code** - Python modules in root
- **Docs** - Markdown files in root

### 2. **Git-Friendly**
- Source code tracked
- Generated files ignored (CSV, PNG)
- Empty directories preserved with `.gitkeep`
- IDE and OS files ignored

### 3. **Consistent Defaults**
- All modules use `data/` for input
- All modules use `charts/` for output
- Clear naming conventions

### 4. **Modular Design**
- Each module can be used independently
- Clear interfaces and default values
- Easy to customize paths

---

## 🚀 Usage Examples

### Recording Prices
```python
from recorder import Recorder

# Uses default: data/btc_prices.csv
recorder = Recorder()
recorder.start()

# Custom path
recorder = Recorder(filename='data/custom.csv')
```

### Analyzing Prices
```python
from analyzer import Analyzer

# Uses defaults: data/btc_prices.csv → charts/price_chart.png
analyzer = Analyzer()
df = analyzer.load_and_plot()

# Custom paths
df = analyzer.load_and_plot(
    csv_file='data/custom.csv',
    output_image='charts/custom_chart.png'
)
```

### Detecting Patterns
```python
from detect import find_pattern
import pandas as pd

df = pd.read_csv('data/btc_prices.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')

patterns = find_pattern(df, jump_threshold=2.0)
```

---

## ✅ Verification

All modules have been tested and verified:

```bash
✓ Analyzer loads correctly
  - Default CSV: data/btc_prices.csv
  - Default Output: charts/price_chart.png

✓ Recorder loads correctly
  - Default Output: data/btc_prices.csv

✓ Pattern detector works correctly
✓ All documentation updated
✓ Directory structure consistent
```

---

## 📋 Checklist for New Features

When adding new features, ensure:

- [ ] Data files go in `data/` directory
- [ ] Generated images go in `charts/` directory
- [ ] Add appropriate `.gitignore` entries
- [ ] Update documentation (README.md & setup.md)
- [ ] Use consistent naming conventions
- [ ] Provide sensible defaults
- [ ] Add tests if applicable

---

*Last Updated: October 19, 2025*
*Version: 1.0 (Structure Standardization)*

