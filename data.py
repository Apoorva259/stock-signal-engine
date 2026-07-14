"""
data.py

Data fetching layer. Standalone module so it can be imported by
main.py and demo.py without creating circular imports with signal_engine.py.
"""

import numpy as np
import pandas as pd
import yfinance as yf


def generate_sample_data(days: int = 300, start_price: float = 1500.0, seed: int = 42) -> pd.DataFrame:
    """Creates fake but realistic-looking daily OHLCV data."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="B")
    days = len(dates)

    daily_returns = rng.normal(loc=0.0004, scale=0.015, size=days)
    close = start_price * (1 + daily_returns).cumprod()

    high = close * (1 + rng.uniform(0, 0.01, size=days))
    low = close * (1 - rng.uniform(0, 0.01, size=days))
    open_ = close * (1 + rng.normal(0, 0.005, size=days))
    volume = rng.integers(500_000, 3_000_000, size=days).astype(float)
    spike_days = rng.choice(days, size=days // 20, replace=False)
    volume[spike_days] *= rng.uniform(2, 4, size=len(spike_days))

    return pd.DataFrame({
        "date": dates,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


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
        df = df.dropna(subset=["close", "open", "high", "low"])
        return df.tail(days).reset_index(drop=True)
    except Exception:
        return None
