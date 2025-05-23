"""
Stock fetching module with optimized caching and batch requests 
to avoid hitting rate limits with Yahoo Finance.
"""
import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
import os
from cachetools import TTLCache

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize cache for stock data
# Cache data for 30 minutes to avoid excessive API calls
CACHE_TTL = 1800  # 30 minutes in seconds
stock_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)

def get_stock_data(symbols, days=30):
    """
    Fetch stock data for one or multiple symbols.
    Uses batch requests and caching to minimize API calls.
    
    Args:
        symbols: String or list of strings with stock symbols
        days: Number of days of history to fetch
        
    Returns:
        Dictionary with symbols as keys and DataFrames as values
    """
    # Convert single symbol to list for consistent handling
    if isinstance(symbols, str):
        symbols = [symbols]
    
    results = {}
    uncached_symbols = []
    
    # Check cache first
    for symbol in symbols:
        cache_key = f"{symbol}_{days}"
        if cache_key in stock_cache:
            results[symbol] = stock_cache[cache_key]
            logging.debug(f"Using cached data for {symbol}")
        else:
            uncached_symbols.append(symbol)
    
    if not uncached_symbols:
        return results
    
    # Batch request for uncached symbols (max 10 at a time to avoid errors)
    for i in range(0, len(uncached_symbols), 10):
        batch = uncached_symbols[i:i+10]
        # Join symbols for batch request
        symbols_str = " ".join(batch)
        
        try:
            logging.info(f"Fetching batch data for: {symbols_str}")
            # Use 1d interval for efficiency
            data = yf.download(
                symbols_str,
                period=f"{days}d",
                interval="1d",
                auto_adjust=True,
                progress=False,
                group_by='ticker'
            )
            
            # If only one symbol was fetched, the data structure is different
            if len(batch) == 1:
                symbol = batch[0]
                # Handle single symbol format
                if not data.empty:
                    df = data.copy()
                    # Ensure we have index as a column
                    df = df.reset_index()
                    results[symbol] = df
                    # Cache the result
                    stock_cache[f"{symbol}_{days}"] = df
                else:
                    results[symbol] = pd.DataFrame()
            else:
                # Handle multi-symbol format
                for symbol in batch:
                    if (symbol,) in data.columns.levels[1]:
                        # Extract data for this symbol
                        df = data.xs(symbol, axis=1, level=1, drop_level=True)
                        # Ensure we have index as a column
                        df = df.reset_index()
                        results[symbol] = df
                        # Cache the result
                        stock_cache[f"{symbol}_{days}"] = df
                    else:
                        results[symbol] = pd.DataFrame()
                        logging.warning(f"No data returned for {symbol}")
            
            # Wait briefly between batches to avoid rate limits
            if i + 10 < len(uncached_symbols):
                time.sleep(1)
                
        except Exception as e:
            logging.error(f"Error fetching batch data: {str(e)}")
            # If batch request fails, try individual requests with backoff
            for symbol in batch:
                results[symbol] = pd.DataFrame()
    
    return results

def get_latest_prices(symbols):
    """
    Get just the latest closing prices for a list of symbols.
    Optimized for minimal data transfer.
    
    Args:
        symbols: List of stock symbols
        
    Returns:
        Dictionary with symbols as keys and prices as values
    """
    result = {}
    
    # Get data for all symbols
    data = get_stock_data(symbols, days=5)  # Just need recent data
    
    # Extract latest prices
    for symbol in symbols:
        try:
            if symbol in data and not data[symbol].empty and 'Close' in data[symbol].columns:
                # Get the latest closing price
                latest_close = data[symbol]['Close'].iloc[-1]
                result[symbol] = float(latest_close) if not pd.isna(latest_close) else None
            else:
                result[symbol] = None
        except Exception as e:
            logging.error(f"Error processing {symbol}: {str(e)}")
            result[symbol] = None
    
    return result

def get_stock_history(symbol, days=180):
    """
    Get historical data for a single stock.
    Wrapper around get_stock_data for backward compatibility.
    
    Args:
        symbol: Stock symbol
        days: Number of days of history
        
    Returns:
        DataFrame with stock data or empty DataFrame if error
    """
    data = get_stock_data(symbol, days)
    return data[symbol] if symbol in data else pd.DataFrame()

def clear_cache():
    """Clear the stock data cache"""
    stock_cache.clear()
    logging.info("Stock data cache cleared")