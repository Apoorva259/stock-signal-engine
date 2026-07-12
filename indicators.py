"""
indicators.py

Hand-written technical indicators. No black-box library — every formula
is visible here, which is exactly what you want to be able to explain
in an interview.

Input to every function: a pandas DataFrame with at least these columns:
    'close', 'high', 'low', 'volume'
(this is the standard shape you'll get back from Zerodha's Kite Connect
historical data API later)
"""

import pandas as pd
import numpy as np


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average — weights recent prices more heavily
    than a simple average. period=50 means 'roughly the last 50 days,
    weighted toward the newest ones'."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (0-100). Measures how sharply a stock
    has been rising vs falling recently.
    Above 70 = 'overbought' (often due for a pullback).
    Below 30 = 'oversold' (often due for a bounce)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val.fillna(50)  # neutral when undefined (e.g. no losses)


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Moving Average Convergence Divergence.
    Returns (macd_line, signal_line, histogram).
    When histogram crosses from negative to positive -> bullish momentum shift.
    When it crosses from positive to negative -> bearish momentum shift."""
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    """Bollinger Bands: a moving average with bands above/below based on
    volatility (standard deviation). Price near the lower band = relatively
    cheap vs recent range. Price near the upper band = relatively expensive."""
    mid = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


def volume_spike_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
    """Today's volume divided by the average volume of the last `period`
    days. A ratio > 1.5 means unusually high interest in the stock today —
    useful to confirm that a price move is 'real' rather than noise."""
    avg_vol = volume.rolling(window=period).mean()
    return volume / avg_vol.replace(0, np.nan)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range — a volatility measure, useful later for
    sizing stop-losses (e.g. 'stop = entry price - 1.5x ATR')."""
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()
