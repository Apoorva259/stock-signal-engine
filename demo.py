"""
demo.py

Run this to see the signal engine work end-to-end, using generated
sample price data (a random walk with some trend, standing in for
real Zerodha data for now).

Once you're ready to connect real data, you'll replace `generate_sample_data()`
with a call to Zerodha's Kite Connect historical data endpoint — the rest
of the pipeline (indicators.py, signal_engine.py) doesn't change at all.

Run with:  python demo.py
"""

import numpy as np
import pandas as pd
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


if __name__ == "__main__":
    df = generate_sample_data()

    scored = compute_composite_score(df)

    print("Last 10 days of signals:\n")
    print(
        scored[["date", "close", "rsi14", "macd_hist", "composite_score", "signal"]]
        .tail(10)
        .to_string(index=False)
    )

    print("\n--- Today's snapshot ---")
    result = latest_signal(df)
    for k, v in result.items():
        print(f"{k}: {v}")
