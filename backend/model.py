# backend/model.py
import pandas as pd
import logging
from datetime import datetime, timedelta
from lightgbm import LGBMRegressor
import numpy as np
import time
import os

# Import our new stock fetcher module
import stock_fetcher

# configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level))

# model configuration from environment variables
n_estimators = int(os.environ.get('MODEL_N_ESTIMATORS', '100'))
learning_rate = float(os.environ.get('MODEL_LEARNING_RATE', '0.05'))
max_depth = int(os.environ.get('MODEL_MAX_DEPTH', '5'))

model = LGBMRegressor(
    n_estimators=n_estimators,
    learning_rate=learning_rate,
    max_depth=max_depth
)
trained = False

def calculate_rsi(data, window=14):
    """
    Calculate the Relative Strength Index (RSI) for the given data.
    """
    delta = data.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_history(symbol, days=180):
    """
    Get historical data for a stock symbol using the optimized stock_fetcher.
    """
    return stock_fetcher.get_stock_history(symbol, days)

TOP_STOCKS = ["AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","BRK-B","JPM","V"]
INDEXES    = {"DOW": "^DJI", "S&P500": "^GSPC"}

def fetch_top_stocks():
    """
    Fetch latest closing prices for top stocks.
    Returns a dictionary of stock symbols and their prices.
    """
    # Using the optimized batch fetching method from stock_fetcher
    return stock_fetcher.get_latest_prices(TOP_STOCKS)

def fetch_index_data():
    """
    Fetch latest index values.
    Returns a dictionary of index names and their values.
    """
    # Using the optimized batch fetching method from stock_fetcher
    index_tickers = list(INDEXES.values())
    prices = stock_fetcher.get_latest_prices(index_tickers)
    
    # Convert from ticker-based to name-based dictionary
    result = {}
    for name, ticker in INDEXES.items():
        result[name] = prices.get(ticker)
        
    return result

def fetch_stock_stats(symbol: str, days: int = 1):
    """Fetch latest stats (last price, high, low, volume) for a stock."""
    try:
        # fetch historical data
        df = get_history(symbol, days)

        # Properly check if dataframe is empty using .empty property
        if df.empty:
            logging.warning(f"No historical data found for {symbol}. Returning default stats.")
            return {
                "last": None,
                "high": None,
                "low": None,
                "volume": None,
                "error": f"No data found for {symbol}."
            }

        # Check if required columns exist
        required_columns = ['Close', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.warning(f"Missing columns {missing_columns} for {symbol}")
            return {
                "last": None,
                "high": None,
                "low": None, 
                "volume": None,
                "error": f"Missing data columns for {symbol}: {', '.join(missing_columns)}"
            }

        # get the latest row of data
        latest = df.iloc[-1]
        
        # Convert all values to native Python types and check for NaN values individually
        return {
            "last": float(latest['Close']) if not pd.isna(latest['Close']) else None,
            "high": float(latest['High']) if not pd.isna(latest['High']) else None,
            "low": float(latest['Low']) if not pd.isna(latest['Low']) else None,
            "volume": int(latest['Volume']) if not pd.isna(latest['Volume']) else None
        }
    
    except Exception as e:
        logging.error(f"Error fetching stock stats for {symbol}: {str(e)}")
        return {
            "last": None,
            "high": None,
            "low": None,
            "volume": None,
            "error": f"Error fetching data for {symbol}: {str(e)}"
        }

def get_ohlc(symbol, days=180):
    """
    Get Open-High-Low-Close data for a stock symbol.
    Returns a list of dictionaries with Date and Close price.
    """
    logging.debug(f"Fetching OHLC data for symbol={symbol}, days={days}")
    df = get_history(symbol, days)
    
    if df.empty:
        logging.error(f"No data returned for symbol={symbol}")
        return []
    
    # Ensure Date column exists
    if 'Date' not in df.columns:
        logging.error(f"Date column not found in dataframe for {symbol}")
        return []
    
    # Ensure Close column exists
    if 'Close' not in df.columns:
        logging.error(f"Close column not found in dataframe for {symbol}")
        return []
    
    logging.debug(f"Processed OHLC data: {len(df)} rows, columns: {df.columns.tolist()}")
    
    # Convert to serializable format (list of dicts)
    result = []
    for _, row in df.iterrows():
        # Convert datetime to string format to ensure it's serializable
        date_str = row['Date'].strftime('%Y-%m-%d') if isinstance(row['Date'], (datetime, pd.Timestamp)) else str(row['Date'])
        
        # Ensure values are native Python types, not numpy types
        result.append({
            'date': date_str,
            'close': float(row['Close'])
        })
    
    logging.debug(f"OHLC result: {len(result)} records")
    return result

def predict_stock(symbol):
    """
    Predict future stock prices using machine learning model.
    Returns a dictionary with prediction results.
    """
    logging.debug(f"Predicting stock prices for symbol={symbol}")
    
    # Input validation
    if not symbol or not isinstance(symbol, str):
        return {
            "error": "Invalid symbol input",
            "symbol": str(symbol) if symbol else ""
        }
    
    global trained, model
    df = get_history(symbol, days=180)
    
    if df.empty:
        logging.error(f"No data available for {symbol}")
        return {
            "error": f"No data available for {symbol}",
            "symbol": symbol
        }
    
    # Calculate technical indicators
    df['RSI'] = calculate_rsi(df['Close'])
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Price_Change'] = df['Close'].pct_change()
    df['Volatility'] = df['Close'].rolling(window=20).std()
    
    # Drop NaN values that arise from calculating indicators
    df = df.dropna()
    
    if df.empty:
        logging.error(f"Insufficient data after processing for {symbol}")
        return {
            "error": f"Insufficient data for {symbol}",
            "symbol": symbol
        }
    
    # Create features
    features = ['RSI', 'MA20', 'MA50', 'Price_Change', 'Volatility']
    X = df[features].values
    prices = df['Close'].values
    
    # train the model if not already trained
    # Using a new model instance for each stock would be better, but keeping global for now
    if not trained:
        model.fit(X, prices)
        trained = True
    
    # Generate predictions
    # For future predictions, use the last known values for our features
    last_features = X[-1:].copy()
    preds = []
    confidence_levels = []
    
    # Simple Monte Carlo simulation for better confidence intervals
    n_simulations = 100
    for i in range(7):
        predictions = []
        for _ in range(n_simulations):
            # Add some random noise to simulate different market conditions
            simulated_features = last_features * np.random.normal(1, 0.02, size=last_features.shape)
            pred = model.predict(simulated_features)[0]
            predictions.append(pred)
        
        # Use median as prediction and calculate confidence intervals from distribution
        median_pred = np.median(predictions)
        preds.append(median_pred)
        low_ci = np.percentile(predictions, 5)
        high_ci = np.percentile(predictions, 95)
        confidence_levels.append({"low": low_ci, "high": high_ci})
    
    # Ensure all values in the response are JSON serializable
    response = {
        "symbol": symbol,
        "past_dates": [d.strftime('%Y-%m-%d') if isinstance(d, (datetime, pd.Timestamp)) else str(d) for d in df['Date']],
        "past_prices": [float(p) for p in prices.tolist()],
        "future_dates": [
            (df['Date'].iloc[-1] + pd.Timedelta(days=i)).strftime('%Y-%m-%d') 
            if isinstance(df['Date'].iloc[-1], (datetime, pd.Timestamp)) 
            else f"Day+{i}"
            for i in range(1, 8)
        ],
        "predicted_prices": [float(p) for p in preds],
        "confidence_intervals": [
            {"low": float(ci["low"]), "high": float(ci["high"])}
            for ci in confidence_levels
        ],
        "hour_prediction": float(preds[0]),
        "day_prediction": float(preds[1]),
        "week_prediction": float(preds[-1]),
    }
    
    return response

def convert_to_native_types(obj):
    """
    Convert numpy and pandas types to native Python types for JSON serialization.
    """
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, (pd.DataFrame)):
        return obj.to_dict(orient='records')
    elif isinstance(obj, (pd.Series)):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: convert_to_native_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(i) for i in obj]
    elif pd.isna(obj):  # Handle NaN/None values
        return None
    else:
        return obj

def get_history_with_retry(symbol, days=180, retries=3, backoff_factor=2):
    """
    Get historical data with retry logic.
    """
    for attempt in range(retries):
        try:
            return get_history(symbol, days)
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {str(e)}")
            if attempt < retries - 1:
                wait_time = backoff_factor ** attempt
                logging.warning(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"Failed to fetch data for {symbol} after {retries} retries.")
                return pd.DataFrame()