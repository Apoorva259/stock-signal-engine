"""
main.py

This turns the signal engine into a real website.

Two jobs happen here:
1. Serve the frontend page (the HTML file in /static) when someone
   visits http://localhost:8000
2. Provide an API endpoint at /api/signal that the page calls to get
   the actual buy/sell data as JSON

Run with:
    uvicorn main:app --reload

Then open http://localhost:8000 in your browser.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from demo import fetch_stock_data
from signal_engine import compute_composite_score, latest_signal

app = FastAPI(title="Stock Signal Engine")

# Allows the frontend page to call this API even during local dev
# where browsers are picky about cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/signal")
def get_signal(symbol: str = "RELIANCE.NS", seed: int = 42):
    """
    Returns today's signal plus the recent price/score history for
    charting. Uses yfinance to fetch real data for the given symbol.
    """
    df = fetch_stock_data(symbol)
    if df is None:
        return {"error": f"No data found for symbol '{symbol}'. Check the ticker and try again."}

    scored = compute_composite_score(df)

    today = latest_signal(df)
    history = scored.tail(60)[["date", "close", "composite_score", "signal"]].copy()
    history["date"] = history["date"].dt.strftime("%Y-%m-%d")

    return {
        "symbol": symbol,
        "today": today,
        "history": history.to_dict(orient="records"),
    }


# Serve the frontend (index.html, etc.) from the /static folder at "/".
# This line must come AFTER the API routes above, or it would swallow them.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
