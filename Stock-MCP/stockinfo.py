from dotenv import load_dotenv
import requests
import os
from fastmcp import FastMCP

load_dotenv()
url = "https://www.alphavantage.co/query"

key = os.getenv("STOCK_API")

if not key:
    raise RuntimeError("Missing ALPHAVANTAGE_API_KEY in environment")

mcp = FastMCP("Stock-MCP")

def _call(params: dict) -> dict:
    params = {**params, "apikey": key}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    # AlphaVantage “errors”
    if "Note" in data:
        # rate limit or usage note
        raise RuntimeError(data["Note"])
    if "Error Message" in data:
        raise RuntimeError(data["Error Message"])
    return data

@mcp.tool()
def global_quote(symbol: str) -> dict:
    """
    Get the latest quote for a stock symbol.
    Returns AlphaVantage 'Global Quote' JSON.
    """
    return _call({"function": "GLOBAL_QUOTE", "symbol": symbol})

@mcp.tool()
def time_series_daily(symbol: str, adjusted: bool = True, outputsize: str = "compact") -> dict:
    """
    Get daily (adjusted or unadjusted) time series.
    outputsize: 'compact' (latest ~100) or 'full' (entire history).
    """
    fn = "TIME_SERIES_DAILY_ADJUSTED" if adjusted else "TIME_SERIES_DAILY"
    return _call({"function": fn, "symbol": symbol, "outputsize": outputsize})

@mcp.tool()
def rsi(symbol: str, interval: str = "daily", time_period: int = 14, series_type: str = "close") -> dict:
    """
    Compute RSI technical indicator via AlphaVantage.
    interval: '1min','5min','15min','30min','60min','daily','weekly','monthly'
    series_type: 'close','open','high','low'
    """
    return _call({
        "function": "RSI",
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type
    })

if __name__ == "__main__":
    mcp.run()