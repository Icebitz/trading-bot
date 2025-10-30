import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional


BINANCE_KLINES_URL = 'https://api.binance.com/api/v3/klines'


def _to_millis(dt: datetime) -> int:

    if dt.tzinfo is None:
        # Assume naive datetimes are UTC
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_minute_prices(
    symbol: str,
    start_time: datetime,
    end_time: datetime,
    session: Optional[requests.Session] = None,
) -> List[Dict]:

    if start_time >= end_time:
        return []

    s = session or requests.Session()

    start_ms = _to_millis(start_time)
    end_ms = _to_millis(end_time)

    # Binance returns up to 1000 candles per request
    limit = 1000
    interval = '1m'

    results: List[Dict] = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': current_start,
            'endTime': end_ms,
            'limit': limit,
        }

        resp = s.get(BINANCE_KLINES_URL, params=params, timeout=15)
        resp.raise_for_status()
        klines = resp.json()

        if not klines:
            break

        for k in klines:
            open_time_ms = k[0]
            close_price = float(k[4])
            open_time_dt = datetime.fromtimestamp(open_time_ms / 1000.0, tz=timezone.utc)
            # We align to the opening minute timestamp for consistency
            results.append({'timestamp': open_time_dt, 'price': round(close_price, 2)})

        # Advance to next batch (next candle after the last returned one)
        last_open_time_ms = klines[-1][0]
        current_start = last_open_time_ms + 60_000

        # Safety: avoid infinite loops
        if len(klines) < limit:
            break

    return results


