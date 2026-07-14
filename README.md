# Stock Signal Engine

A technical analysis engine that computes composite buy/sell signals for stocks and mutual funds using real market data from Yahoo Finance. Generates a weighted score from -100 (strong sell) to +100 (strong buy) by combining multiple independent technical indicators.

## Features

- **Composite Scoring System** — Combines Trend, Momentum, Volatility, and Volume indicators into a single weighted score
- **Live Data** — Fetches real-time OHLCV data via Yahoo Finance
- **Instant Search** — Autocomplete search across all symbols available on Yahoo Finance (stocks, ETFs, mutual funds)
- **Web Dashboard** — Dark-themed UI with interactive charts powered by Chart.js
- **CLI Support** — Run signals from the terminal for quick analysis
- **Error Handling** — Graceful fallbacks for invalid or missing symbols

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python 3, FastAPI, Uvicorn |
| Data | yfinance, Pandas, NumPy |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Deployment | Render (or any ASGI-compatible host) |

## Architecture

```
User Input → /api/search (yfinance.Search) → Autocomplete dropdown
          → /api/signal  (yfinance historical data)
                ↓
          indicators.py (EMA, RSI, MACD, Bollinger Bands, ATR, Volume)
                ↓
          signal_engine.py (weighted composite score -100 to +100)
                ↓
          JSON response (signal, score, components, explanation, chart history)
```

### Scoring Breakdown

| Component | Weight | What It Measures |
|---|---|---|
| Trend | 35% | EMA50 vs EMA200 crossover, price position relative to EMA50 |
| Momentum | 30% | RSI (14) + MACD histogram direction |
| Volatility | 15% | Price position inside Bollinger Bands |
| Volume | 20% | Volume spike ratio confirmed by price direction |

### Signal Thresholds

| Score Range | Signal |
|---|---|
| +40 to +100 | STRONG BUY |
| +15 to +39 | BUY |
| -14 to +14 | HOLD |
| -39 to -15 | SELL |
| -100 to -40 | STRONG SELL |

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/Apoorva259/stock-signal-engine.git
cd stock-signal-engine
pip install -r requirements.txt
python tickers.py          # generate ticker list (optional, search works live)
```

### Run the Web Interface

```bash
uvicorn main:app --reload
```

Open http://localhost:8000 in your browser.

### Run from CLI

```bash
python demo.py                     # defaults to RELIANCE.NS
python demo.py AAPL                # US stocks
python demo.py TCS.NS              # NSE stocks (use .NS suffix)
python demo.py "Rama Steel"        # mutual funds and fuzzy names work too
```

## Project Structure

```
├── main.py              # FastAPI web server (API + static files)
├── data.py              # Data fetching layer (yfinance)
├── signal_engine.py     # Composite scoring logic
├── indicators.py        # Technical indicator implementations
├── demo.py              # CLI entry point
├── tickers.py           # Ticker list generator (optional)
├── requirements.txt     # Python dependencies
└── static/
    ├── index.html       # Web dashboard
    └── tickers.json     # Pre-generated ticker list
```

## API Endpoints

### `GET /api/signal?symbol=AAPL`

Returns today's signal, component scores, explanation, and 60-day history.

### `GET /api/search?q=reliance`

Returns matching symbols from Yahoo Finance live search.

## Deployment

The project is configured for deployment on Render. The service starts automatically with:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## License

MIT
