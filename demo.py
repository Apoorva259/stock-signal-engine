"""
demo.py

Run this to see the signal engine work end-to-end, fetches real
OHLCV data via yfinance.

Usage:
    python demo.py              # defaults to RELIANCE.NS
    python demo.py TCS.NS       # fetch a specific symbol
    python demo.py AAPL         # US stocks work too
"""

from data import fetch_stock_data
from signal_engine import compute_composite_score, latest_signal


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
