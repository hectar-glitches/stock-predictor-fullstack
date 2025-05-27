# backend/stock_fetcher.py
import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
import time
import os
from functools import lru_cache
import json
from pathlib import Path

# Configure cache directory
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Configure how long cache entries should be considered valid (in seconds)
CACHE_TTL = {
    "history": 3600,  # 1 hour for historical data
    "latest": 300,    # 5 minutes for latest prices
}

def get_cache_path(symbol, type="history", days=180):
    """Generate a cache file path for the given parameters."""
    return CACHE_DIR / f"{symbol}_{type}_{days}.json"

def is_cache_valid(cache_path, ttl):
    """Check if cache file exists and is not expired."""
    if not cache_path.exists():
        return False
    
    # Check if file is newer than TTL
    file_age = time.time() - os.path.getmtime(cache_path)
    return file_age < ttl

def save_to_cache(data, cache_path):
    """Save data to cache file."""
    try:
        # Prepare the data with timestamp
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }
        
        # Convert DataFrame to dict for JSON serialization
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, pd.DataFrame):
                    cache_data["data"][k] = v.to_dict(orient="split")
        elif isinstance(data, pd.DataFrame):
            cache_data["data"] = data.to_dict(orient="split")
                
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
            
        logging.debug(f"Saved data to cache: {cache_path}")
    except Exception as e:
        logging.warning(f"Failed to save to cache: {e}")

def load_from_cache(cache_path):
    """Load data from cache file."""
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
            
        data = cache_data.get("data")
        
        # Convert dict back to DataFrame if needed
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict) and "index" in v and "data" in v:
                    data[k] = pd.DataFrame(data=v["data"], index=v["index"], columns=v["columns"])
        elif isinstance(data, dict) and "index" in data and "data" in data:
            data = pd.DataFrame(data=data["data"], index=data["index"], columns=data["columns"])
            
        logging.debug(f"Loaded data from cache: {cache_path}")
        return data
    except Exception as e:
        logging.warning(f"Failed to load from cache: {e}")
        return None

def get_stock_history(symbol, days=180):
    """Get historical data for a stock symbol with caching."""
    cache_path = get_cache_path(symbol, "history", days)
    
    # Try to load from cache first
    if is_cache_valid(cache_path, CACHE_TTL["history"]):
        data = load_from_cache(cache_path)
        if data is not None and not isinstance(data, pd.DataFrame) and not data.empty:
            return data
    
    # If cache miss or invalid, fetch fresh data
    try:
        logging.info(f"Fetching historical data for {symbol} (days={days})")
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        
        stock = yf.Ticker(symbol)
        df = stock.history(period=f"{days}d")
        
        if df.empty:
            logging.warning(f"No data returned for {symbol}")
            return pd.DataFrame()
        
        # Reset index to make Date a column
        df = df.reset_index()
        
        # Cache the result
        save_to_cache(df, cache_path)
        
        return df
    
    except Exception as e:
        logging.error(f"Error fetching history for {symbol}: {str(e)}")
        return pd.DataFrame()

def get_stock_data(symbols, days=1):
    """Get stock data for one or multiple symbols."""
    result = {}
    
    # Convert to list if single symbol
    if isinstance(symbols, str):
        symbols = [symbols]
    
    for symbol in symbols:
        result[symbol] = get_stock_history(symbol, days)
        
    return result

def get_latest_prices(symbols):
    """Get latest closing prices for a list of stock symbols."""
    cache_path = get_cache_path("batch", "latest", len(symbols))
    
    # Try to load from cache first
    if is_cache_valid(cache_path, CACHE_TTL["latest"]):
        prices = load_from_cache(cache_path)
        if prices is not None:
            return prices
    
    # If cache miss or invalid, fetch fresh data
    prices = {}
    
    try:
        logging.info(f"Fetching latest prices for {len(symbols)} symbols")
        
        # Fetch data in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            
            # Add a small delay between batches
            if i > 0:
                time.sleep(1)
                
            logging.debug(f"Fetching batch: {', '.join(batch)}")
            
            for symbol in batch:
                try:
                    df = get_stock_history(symbol, days=5)  # Get 5 days to ensure we have some data
                    
                    if not df.empty and 'Close' in df.columns:
                        # Get the latest price
                        latest_price = df['Close'].iloc[-1]
                        prices[symbol] = float(latest_price) if not pd.isna(latest_price) else None
                    else:
                        prices[symbol] = None
                        
                except Exception as e:
                    logging.error(f"Error fetching latest price for {symbol}: {str(e)}")
                    prices[symbol] = None
    
        # Cache the results
        save_to_cache(prices, cache_path)
        
        return prices
        
    except Exception as e:
        logging.error(f"Error fetching latest prices: {str(e)}")
        return {symbol: None for symbol in symbols}