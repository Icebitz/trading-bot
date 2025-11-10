# 📈 BTC Trading Bot

A Python toolkit for collecting minute-level BTC/USDT data, analysing market structure, and exercising a moving-average trading workflow end-to-end.

## ✨ Features

- **Live price recorder** pulling Binance ticker data with automatic gap detection and optional historical backfill.
- **Signal engine** using configurable moving-average crossover logic.
- **Strategy backtester** with portfolio value tracking and summary metrics.
- **Visual reporting** that plots prices, signals, and equity curves.
- **Pattern scanner** for volatility and sharp-move detection.
- **Live signal monitor** that can push BUY/SELL alerts to Telegram.

---

## 🚀 Quick Start

```bash
# 0) Clone (optional if you're already inside the repo)
git clone https://github.com/Icebitz/trading-bot.git
cd trading-bot

# 1) Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2) Collect BTC/USDT prices once per minute
python modules/recorder.py               # writes to data/btc_prices.csv

# 3) Create moving-average signals & export to CSV
python test_ma_strategy.py               # outputs data/btc_signals.csv

# 4) Backtest the strategy and store portfolio values
python test_backtester.py                # outputs data/btc_backtest.csv

# 5) Generate charts / analysis artefacts
python modules/analyzer.py               # price trend chart
python test_visualizer.py                # composite equity + signal chart

# 6) Explore volatility & intraday patterns
python test_detect.py
```

---

## 🧭 Typical Workflow

1. **Record data** with `modules/recorder.py` (leave it running to build `data/btc_prices.csv`).
2. **Optionally backfill missing minutes** by importing `modules.historical.fetch_minute_prices` in your own scripts.
3. **Derive signals** via `test_ma_strategy.py`, which persists moving averages, crossover signals, and cleaned pricing to `data/btc_signals.csv`.
4. **Run a backtest** with `test_backtester.py` to append portfolio values and daily returns (`data/btc_backtest.csv`).
5. **Visualise** results using `modules/analyzer.py` and `modules/visualizer.plot_strategy_results`, storing charts in `charts/`.
6. **Inspect patterns** with `modules/detector.find_pattern` or the helper script `test_detect.py`.

---

## 📡 Live Signal Monitor

`live_signal_monitor.py` watches `data/btc_prices.csv`, recomputes MAs every minute, and prints/pushes new BUY/SELL signals. To enable Telegram alerts, set:

```bash
export TELEGRAM_BOT_TOKEN="xxx"
export TELEGRAM_CHAT_ID="yyy"
python live_signal_monitor.py
```

The script throttles duplicate alerts and logs each actionable crossover with the current price and MA context.

---

## 📊 Artefacts & Outputs

| File | How it is created | Contents |
| --- | --- | --- |
| `data/btc_prices.csv` | `modules/recorder.py` | Minute-level BTC/USDT price history |
| `data/btc_signals.csv` | `test_ma_strategy.py` | Prices, short/long MAs, and signals |
| `data/btc_backtest.csv` | `test_backtester.py` | Portfolio value series and performance stats |
| `charts/price_chart.png` | `modules/analyzer.py` | Last-day price plot |
| `charts/strategy_results.png` | `test_visualizer.py` | Price, MAs, signals, and equity curve |

---

## 📦 Components & Modules

- `modules/recorder.py` — resilient live price ingestion.
- `modules/historical.py` — Binance 1m kline backfill helper.
- `modules/ma_strategy.py` — moving-average crossover logic.
- `modules/backtester.py` — capital, drawdown, and win-rate calculations.
- `modules/analyzer.py` — charting utility for recent price action.
- `modules/detector.py` — pattern/volatility summaries.
- `modules/visualizer.py` — plotting helper for combined signal/equity charts.
- `live_signal_monitor.py` — real-time monitoring + optional Telegram notifications.

---

## ✅ Testing & Validation

Lightweight smoke scripts exist for each stage. Run them individually (as shown above) or via:

```bash
python -m pytest
```

Pytest will discover the `test_*.py` files; keep in mind that these scripts print artefacts rather than strict assertions, so treat them as integration smoke tests.

---

## 📂 Project Structure

```
trading-bot/
├── modules/                # Core application modules
│   ├── analyzer.py
│   ├── backtester.py
│   ├── detector.py
│   ├── historical.py
│   ├── ma_strategy.py
│   ├── recorder.py
│   └── visualizer.py
├── data/                   # CSV outputs (created at runtime)
├── charts/                 # Generated chart images
├── docs/                   # Extended documentation
├── live_signal_monitor.py  # Real-time alert runner
├── test_backtester.py
├── test_detect.py
├── test_ma_strategy.py
├── test_visualizer.py
├── requirements.txt
└── README.md
```

---

## 📖 Additional Docs

- `docs/setup.md` — expanded environment and Git setup guidance.
- `docs/observations.md` — log of market learnings and experiments.

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Pandas**, **NumPy**
- **Matplotlib**
- **Requests**
- **Schedule**

---

## ⚠️ Disclaimer

This project is for educational and research purposes only and does **not** constitute financial advice. Use at your own risk.

---

**Built with ❤️ for crypto enthusiasts**

*Last Updated: November 10, 2025*

