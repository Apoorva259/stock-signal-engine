"""
demo.py

Run this to see the signal engine work end-to-end, fetches real
OHLCV data via yfinance. Falls back to synthetic sample data if
the symbol isn't found.

Usage:
    python demo.py              # defaults to RELIANCE.NS
    python demo.py TCS.NS       # fetch a specific symbol
    python demo.py AAPL         # US stocks work too
"""

import numpy as np
import pandas as pd
import yfinance as yf
from signal_engine import compute_composite_score, latest_signal


def generate_sample_data(days: int = 300, start_price: float = 1500.0, seed: int = 42) -> pd.DataFrame:
    """Creates fake but realistic-looking daily OHLCV data, standing in
    for a real stock like RELIANCE or TCS until you plug in Kite Connect."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="B")
    days = len(dates)  # guard against off-by-one from date_range/freq edge cases

    # random walk with slight upward drift, plus some volatility clustering
    daily_returns = rng.normal(loc=0.0004, scale=0.015, size=days)
    close = start_price * (1 + daily_returns).cumprod()

    high = close * (1 + rng.uniform(0, 0.01, size=days))
    low = close * (1 - rng.uniform(0, 0.01, size=days))
    open_ = close * (1 + rng.normal(0, 0.005, size=days))
    volume = rng.integers(500_000, 3_000_000, size=days).astype(float)
    # occasionally spike volume, to make the volume_score logic meaningful
    spike_days = rng.choice(days, size=days // 20, replace=False)
    volume[spike_days] *= rng.uniform(2, 4, size=len(spike_days))

    df = pd.DataFrame({
        "date": dates,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })
    return df


def fetch_stock_data(symbol: str, days: int = 300) -> pd.DataFrame | None:
    """Fetches real historical OHLCV data using yfinance.
    Returns None if the symbol isn't found."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=f"{days + 30}d")
        if df.empty:
            return None
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        keep = {"date", "open", "high", "low", "close", "volume"}
        df = df[[c for c in df.columns if c in keep]]
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        return df.tail(days).reset_index(drop=True)
    except Exception:
        return None


if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    df = fetch_stock_data(symbol)
    if df is None:
        print(f"Error: no data found for symbol '{symbol}'")
        sys.exit(1)

    scored = compute_composite_score(df)

    print(f"Last 10 days of signals for {symbol}:\n")
    print(
        scored[["date", "close", "rsi14", "macd_hist", "composite_score", "signal"]]
        .tail(10)
        .to_string(index=False)
    )

    print("\n--- Today's snapshot ---")
    result = latest_signal(df)
    for k, v in result.items():
        print(f"{k}: {v}")
