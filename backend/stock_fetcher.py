# backend/stock_fetcher.py
import yfinance as yf
import pandas as pd
import logging
import time
from pathlib import Path
from utils.cache_manager import CacheManager
from utils.rate_limiter import RateLimiter

# Initialize cache manager and rate limiter
CACHE_TTL = {
    "history": 3600,  # 1 hour for historical data
    "latest": 300,    # 5 minutes for latest prices
}
cache_manager = CacheManager(Path(__file__).parent / "cache", CACHE_TTL)
rate_limiter = RateLimiter(max_calls=5, time_window=60)  # 5 calls per minute

@rate_limiter.limit
def get_stock_history(symbol: str, days: int = 180) -> pd.DataFrame:
    """Get historical data for a stock symbol with caching."""
    cache_path = cache_manager.get_cache_path(symbol, "history", days)
    
    # Try to load from cache first
    if cache_manager.is_valid(cache_path, CACHE_TTL["history"]):
        data = cache_manager.load(cache_path)
        if data is not None and not data.empty:
            return data
    
    # If cache miss or invalid, fetch fresh data
    try:
        logging.info(f"Fetching historical data for {symbol} (days={days})")
        stock = yf.Ticker(symbol)
        df = stock.history(period=f"{days}d")
        
        if df.empty:
            logging.warning(f"No data returned for {symbol}")
            return pd.DataFrame()
        
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Cache the result
        cache_manager.save(df, cache_path)
        return df
    
    except Exception as e:
        logging.error(f"Error fetching history for {symbol}: {str(e)}")
        return pd.DataFrame()

def get_stock_data(symbols, days=1):
    """Get stock data for one or multiple symbols."""
    result = {}
    symbols = [symbols] if isinstance(symbols, str) else symbols
    
    for symbol in symbols:
        result[symbol] = get_stock_history(symbol, days)
        
    return result

@rate_limiter.limit
def get_latest_prices(symbols):
    """Get latest closing prices for a list of stock symbols."""
    cache_path = cache_manager.get_cache_path("batch", "latest", len(symbols))
    
    # Try to load from cache first
    if cache_manager.is_valid(cache_path, CACHE_TTL["latest"]):
        prices = cache_manager.load(cache_path)
        if prices is not None:
            return prices
    
    # If cache miss or invalid, fetch fresh data
    prices = {}
    
    try:
        logging.info(f"Fetching latest prices for {len(symbols)} symbols")
        
        # Batch fetch to minimize API calls
        symbols_str = " ".join(symbols)
        data = yf.download(symbols_str, period="1d", group_by='ticker', progress=False)
        
        # Process results
        for symbol in symbols:
            try:
                if len(symbols) == 1:
                    close_price = data['Close'].iloc[-1]
                else:
                    close_price = data[symbol]['Close'].iloc[-1]
                prices[symbol] = float(close_price) if not pd.isna(close_price) else None
            except Exception as e:
                logging.error(f"Error processing price for {symbol}: {str(e)}")
                prices[symbol] = None
    
        # Cache the results
        cache_manager.save(prices, cache_path)
        return prices
        
    except Exception as e:
        logging.error(f"Error fetching latest prices: {str(e)}")
        return {symbol: None for symbol in symbols}