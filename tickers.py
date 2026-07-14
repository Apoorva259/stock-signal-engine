"""
tickers.py

Generates static/tickers.json — a curated list of stock symbols
for the autocomplete dropdown. Run this whenever you want to
refresh the list.

Usage:
    python tickers.py
"""

import json
from pathlib import Path

# NIFTY 50 stocks (.NS for NSE)
NSE = [
    ("RELIANCE.NS", "Reliance Industries"),
    ("TCS.NS", "Tata Consultancy Services"),
    ("HDFCBANK.NS", "HDFC Bank"),
    ("INFY.NS", "Infosys"),
    ("ICICIBANK.NS", "ICICI Bank"),
    ("SBIN.NS", "State Bank of India"),
    ("BHARTIARTL.NS", "Bharti Airtel"),
    ("ITC.NS", "ITC Ltd"),
    ("WIPRO.NS", "Wipro Ltd"),
    ("HINDUNILVR.NS", "Hindustan Unilever"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
    ("LT.NS", "Larsen & Toubro"),
    ("BAJFINANCE.NS", "Bajaj Finance"),
    ("AXISBANK.NS", "Axis Bank"),
    ("TITAN.NS", "Titan Company"),
    ("ASIANPAINT.NS", "Asian Paints"),
    ("MARUTI.NS", "Maruti Suzuki India"),
    ("SUNPHARMA.NS", "Sun Pharmaceutical"),
    ("ULTRACEMCO.NS", "UltraTech Cement"),
    ("NTPC.NS", "NTPC Ltd"),
    ("POWERGRID.NS", "Power Grid Corporation"),
    ("M&M.NS", "Mahindra & Mahindra"),
    ("TRENT.NS", "Trent Ltd"),
    ("BAJAJFINSV.NS", "Bajaj Finserv"),
    ("HCLTECH.NS", "HCL Technologies"),
    ("ADANIPORTS.NS", "Adani Ports & SEZ"),
    ("JSWSTEEL.NS", "JSW Steel"),
    ("TATASTEEL.NS", "Tata Steel"),
    ("COALINDIA.NS", "Coal India"),
    ("ONGC.NS", "Oil & Natural Gas Corp"),
    ("BRITANNIA.NS", "Britannia Industries"),
    ("NESTLEIND.NS", "Nestle India"),
    ("HINDALCO.NS", "Hindalco Industries"),
    ("TECHM.NS", "Tech Mahindra"),
    ("BEL.NS", "Bharat Electronics"),
    ("ADANIENT.NS", "Adani Enterprises"),
    ("EICHERMOT.NS", "Eicher Motors"),
    ("BAJAJ-AUTO.NS", "Bajaj Auto"),
    ("HEROMOTOCO.NS", "Hero MotoCorp"),
    ("CIPLA.NS", "Cipla"),
    ("DRREDDY.NS", "Dr Reddy's Laboratories"),
    ("DIVISLAB.NS", "Divi's Laboratories"),
    ("APOLLOHOSP.NS", "Apollo Hospitals"),
    ("GRASIM.NS", "Grasim Industries"),
    ("BPCL.NS", "Bharat Petroleum"),
    ("SBILIFE.NS", "SBI Life Insurance"),
    ("HDFCLIFE.NS", "HDFC Life Insurance"),
    ("INDUSINDBK.NS", "IndusInd Bank"),
    ("TATAMOTORS.NS", "Tata Motors"),
    ("SHRIRAMFIN.NS", "Shriram Finance"),
]

# Additional popular NSE stocks
NSE_EXTRA = [
    ("VEDL.NS", "Vedanta Ltd"),
    ("IOC.NS", "Indian Oil Corp"),
    ("GAIL.NS", "GAIL India"),
    ("ZOMATO.NS", "Zomato Ltd"),
    ("PNB.NS", "Punjab National Bank"),
    ("BANKBARODA.NS", "Bank of Baroda"),
    ("YESBANK.NS", "Yes Bank"),
    ("IDFCFIRSTB.NS", "IDFC First Bank"),
    ("DMART.NS", "Avenue Supermarts"),
    ("TATACONSUM.NS", "Tata Consumer Products"),
    ("DABUR.NS", "Dabur India"),
    ("MARICO.NS", "Marico Ltd"),
    ("PIDILITIND.NS", "Pidilite Industries"),
    ("HAVELLS.NS", "Havells India"),
    ("AMBUJACEM.NS", "Ambuja Cements"),
    ("TVSMOTOR.NS", "TVS Motor Company"),
    ("MCDOWELL-N.NS", "United Spirits"),
    ("BANDHANBNK.NS", "Bandhan Bank"),
    ("COLPAL.NS", "Colgate-Palmolive India"),
    ("GODREJCP.NS", "Godrej Consumer Products"),
    ("TORNTPHARM.NS", "Torrent Pharmaceuticals"),
    ("LICHSGFIN.NS", "LIC Housing Finance"),
    ("NHPC.NS", "NHPC Ltd"),
    ("IRCTC.NS", "IRCTC"),
    ("HAL.NS", "Hindustan Aeronautics"),
]

# Major US stocks
US = [
    ("AAPL", "Apple Inc"),
    ("MSFT", "Microsoft Corp"),
    ("GOOGL", "Alphabet Inc"),
    ("AMZN", "Amazon.com Inc"),
    ("META", "Meta Platforms"),
    ("NVDA", "NVIDIA Corp"),
    ("TSLA", "Tesla Inc"),
    ("JPM", "JPMorgan Chase"),
    ("V", "Visa Inc"),
    ("JNJ", "Johnson & Johnson"),
    ("WMT", "Walmart Inc"),
    ("MA", "Mastercard Inc"),
    ("PG", "Procter & Gamble"),
    ("XOM", "Exxon Mobil Corp"),
    ("KO", "Coca-Cola Co"),
    ("PEP", "PepsiCo Inc"),
    ("MRK", "Merck & Co"),
    ("ABBV", "AbbVie Inc"),
    ("ORCL", "Oracle Corp"),
    ("AMD", "Advanced Micro Devices"),
    ("INTC", "Intel Corp"),
    ("BA", "Boeing Co"),
    ("DIS", "Walt Disney Co"),
    ("NFLX", "Netflix Inc"),
    ("ADBE", "Adobe Inc"),
    ("CRM", "Salesforce Inc"),
    ("UBER", "Uber Technologies"),
    ("SQ", "Block Inc"),
    ("PYPL", "PayPal Holdings"),
    ("SNAP", "Snap Inc"),
    ("SPOT", "Spotify Technology"),
    ("TSM", "Taiwan Semiconductor"),
    ("BABA", "Alibaba Group"),
    ("NIO", "NIO Inc"),
    ("PLTR", "Palantir Technologies"),
    ("COIN", "Coinbase Global"),
    ("HOOD", "Robinhood Markets"),
]

# Popular ETFs
ETFS = [
    ("SPY", "SPDR S&P 500 ETF"),
    ("QQQ", "Invesco QQQ Trust"),
    ("VTI", "Vanguard Total Stock Market"),
    ("IVV", "iShares Core S&P 500"),
    ("VOO", "Vanguard S&P 500 ETF"),
    ("BND", "Vanguard Total Bond Market"),
    ("GLD", "SPDR Gold Shares"),
    ("SLV", "iShares Silver Trust"),
    ("EEM", "iShares MSCI Emerging Markets"),
    ("VNQ", "Vanguard Real Estate ETF"),
]


def main():
    tickers = []
    for symbol, name in NSE + NSE_EXTRA:
        tickers.append({"symbol": symbol, "name": name, "exchange": "NSE"})
    for symbol, name in US:
        tickers.append({"symbol": symbol, "name": name, "exchange": "NASDAQ/NYSE"})
    for symbol, name in ETFS:
        tickers.append({"symbol": symbol, "name": name, "exchange": "US ETF"})

    out_path = Path(__file__).parent / "static" / "tickers.json"
    out_path.write_text(json.dumps(tickers, indent=2))
    print(f"Generated {out_path} with {len(tickers)} tickers.")


if __name__ == "__main__":
    main()
