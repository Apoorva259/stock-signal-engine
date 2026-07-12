"""
signal_engine.py

Combines the raw indicators into a single composite score from -100
(strong sell) to +100 (strong buy), instead of a rigid if/else chain.

Why a weighted score instead of a simple rule?
Because a single indicator lies to you all the time (RSI can stay
"oversold" for weeks in a downtrend). Combining several independent
signals and requiring them to agree is a more robust idea, and it's
also the part of this project that's genuinely interesting to talk
about in an interview.
"""

import pandas as pd
from indicators import ema, rsi, macd, bollinger_bands, volume_spike_ratio, atr


# How much each component contributes to the final score.
# These are a reasonable starting point — tune them once you've
# backtested against your own holdings.
WEIGHTS = {
    "trend": 35,      # EMA50 vs EMA200 + price position
    "momentum": 30,   # RSI + MACD histogram
    "volatility": 15, # Bollinger Band position
    "volume": 20,     # volume confirmation
}


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Takes raw OHLCV data, returns it with all indicator columns attached."""
    out = df.copy()
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["rsi14"] = rsi(out["close"], 14)
    macd_line, signal_line, hist = macd(out["close"])
    out["macd_line"] = macd_line
    out["macd_signal"] = signal_line
    out["macd_hist"] = hist
    upper, mid, lower = bollinger_bands(out["close"])
    out["bb_upper"] = upper
    out["bb_mid"] = mid
    out["bb_lower"] = lower
    out["vol_ratio"] = volume_spike_ratio(out["volume"])
    out["atr14"] = atr(out)
    return out


def _trend_score(row) -> float:
    """+100 if strongly uptrending, -100 if strongly downtrending."""
    score = 0
    if row["ema50"] > row["ema200"]:
        score += 60   # golden-cross-like structure
    else:
        score -= 60
    if row["close"] > row["ema50"]:
        score += 40
    else:
        score -= 40
    return max(min(score, 100), -100)


def _momentum_score(row) -> float:
    score = 0
    # RSI: below 30 is bullish (oversold, potential bounce),
    # above 70 is bearish (overbought, potential pullback)
    if row["rsi14"] < 30:
        score += 50
    elif row["rsi14"] > 70:
        score -= 50
    else:
        # linear scale between 30-70, midpoint 50 = neutral
        score += (50 - row["rsi14"]) * 1.25

    # MACD histogram: positive and rising = bullish momentum
    if row["macd_hist"] > 0:
        score += 50
    else:
        score -= 50
    return max(min(score, 100), -100)


def _volatility_score(row) -> float:
    """Where is price sitting inside its Bollinger Band range?
    Near lower band -> relatively cheap -> bullish tilt.
    Near upper band -> relatively expensive -> bearish tilt."""
    band_width = row["bb_upper"] - row["bb_lower"]
    if band_width == 0 or pd.isna(band_width):
        return 0
    position = (row["close"] - row["bb_lower"]) / band_width  # 0 to 1
    # position=0 (at lower band) -> +100, position=1 (at upper band) -> -100
    score = (0.5 - position) * 200
    return max(min(score, 100), -100)


def _volume_score(row) -> float:
    """High volume on a day the price rose = bullish confirmation.
    High volume on a day the price fell = bearish confirmation.
    Low volume = weak signal, low confidence, score pulled toward 0."""
    if pd.isna(row["vol_ratio"]):
        return 0
    price_up = row["close"] > row.get("prev_close", row["close"])
    magnitude = min(row["vol_ratio"], 3.0) / 3.0 * 100  # cap influence
    return magnitude if price_up else -magnitude


def compute_composite_score(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a 'composite_score' and 'signal' column to the dataframe."""
    out = compute_indicators(df)
    out["prev_close"] = out["close"].shift(1)

    out["raw_trend"] = out.apply(_trend_score, axis=1)
    out["raw_momentum"] = out.apply(_momentum_score, axis=1)
    out["raw_volatility"] = out.apply(_volatility_score, axis=1)
    out["raw_volume"] = out.apply(_volume_score, axis=1)

    total_weight = sum(WEIGHTS.values())
    out["composite_score"] = (
        out["raw_trend"] * WEIGHTS["trend"]
        + out["raw_momentum"] * WEIGHTS["momentum"]
        + out["raw_volatility"] * WEIGHTS["volatility"]
        + out["raw_volume"] * WEIGHTS["volume"]
    ) / total_weight

    def label(score):
        if score >= 40:
            return "STRONG BUY"
        elif score >= 15:
            return "BUY"
        elif score <= -40:
            return "STRONG SELL"
        elif score <= -15:
            return "SELL"
        else:
            return "HOLD"

    out["signal"] = out["composite_score"].apply(label)
    return out


def generate_explanation(row) -> str:
    """Returns a short human-readable explanation for the signal."""
    parts = []
    if float(row["raw_trend"]) > 0:
        parts.append("uptrend (price above EMAs)")
    elif float(row["raw_trend"]) < 0:
        parts.append("downtrend (price below EMAs)")

    rsi = float(row["rsi14"])
    if rsi < 30:
        parts.append("oversold RSI")
    elif rsi > 70:
        parts.append("overbought RSI")

    if float(row["macd_hist"]) > 0:
        parts.append("bullish MACD")
    else:
        parts.append("bearish MACD")

    bb_width = float(row["bb_upper"] - row["bb_lower"])
    if bb_width != 0:
        bb_pos = float(row["close"] - row["bb_lower"]) / bb_width
        if bb_pos < 0.2:
            parts.append("near lower Bollinger Band")
        elif bb_pos > 0.8:
            parts.append("near upper Bollinger Band")

    vol = float(row["vol_ratio"])
    if vol > 1.5:
        parts.append(f"high volume ({vol:.1f}x avg)")

    return ", ".join(parts) if parts else "mixed signals"


def latest_signal(df: pd.DataFrame) -> dict:
    """Convenience function: run the engine and return just today's result."""
    scored = compute_composite_score(df)
    last = scored.iloc[-1]
    return {
        "signal": str(last["signal"]),
        "score": round(float(last["composite_score"]), 1),
        "close": round(float(last["close"]), 2),
        "rsi": round(float(last["rsi14"]), 1),
        "trend": "up" if float(last["ema50"]) > float(last["ema200"]) else "down",
        "components": {
            "trend": round(float(last["raw_trend"]), 1),
            "momentum": round(float(last["raw_momentum"]), 1),
            "volatility": round(float(last["raw_volatility"]), 1),
            "volume": round(float(last["raw_volume"]), 1),
        },
        "weights": {k: int(v) for k, v in WEIGHTS.items()},
        "explanation": generate_explanation(last),
    }
