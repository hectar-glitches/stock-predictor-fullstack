# backend/model.py
import yfinance as yf
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
import logging
logging.basicConfig(level=logging.DEBUG)


model = LGBMRegressor(n_estimators=100, learning_rate=0.05, max_depth=5)
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
    try:
        df = yf.download(symbol, period=f"{days}d", interval="1d")[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        logging.debug("Data fetched for %s:\n%s", symbol, df.head())  # Log the first few rows
        return df.reset_index(drop=True)
    except Exception as e:
        logging.error("Error fetching historical data for %s: %s", symbol, str(e))
        return pd.DataFrame()  # Return an empty DataFrame on error

TOP_STOCKS = ["AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","BRK-B","JPM","V"]
INDEXES    = {"DOW": "^DJI", "S&P500": "^GSPC"}

def fetch_top_stocks():
    return { sym: get_history(sym,30)['Close'].iloc[-1] for sym in TOP_STOCKS }

def fetch_index_data():
    return { name: get_history(ticker,30)['Close'].iloc[-1] 
             for name,ticker in INDEXES.items() }

def fetch_stock_stats(symbol, days=1):
    """
    Return last, high, low, volume, plus change & %change over 'days' window.
    """
    df = get_history(symbol, days+1)  # today + N days back
    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    last   = float(latest['Close'])
    high   = float(latest['High'])
    low    = float(latest['Low'])
    vol    = int(latest['Volume'])
    change = last - float(prev['Close'])
    pct    = (change / float(prev['Close'])) * 100
    return {
        "symbol": symbol,
        "last": last,
        "high": high,
        "low": low,
        "volume": vol,
        "change": change,
        "pct": pct
    }

def get_ohlc(symbol, days=180):
    logging.debug("Fetching OHLC data for symbol=%s, days=%d", symbol, days)
    df = get_history(symbol, days)
    if df.empty:
        logging.error("No data returned for symbol=%s", symbol)
        return []
    logging.debug("Processed OHLC data:\n%s", df.head())
    result = df[['Date', 'Close']].to_dict(orient='records')
    logging.debug("OHLC result:\n%s", result)
    return result

def predict_stock(symbol):
    logging.debug("Predicting stock prices for symbol=%s", symbol)
    global trained, model
    df = get_history(symbol, days=180)
    prices = df['Close'].values
    X = np.arange(len(prices)).reshape(-1, 1)

    # train the model if not already trained
    if not trained:
        model.fit(X, prices)
        trained = True

    # generate predictions for the next hour, day, and week
    future_X = np.arange(len(prices), len(prices) + 7).reshape(-1, 1)
    preds = model.predict(future_X).tolist()

    # add confidence intervals (e.g., ±5% of the predicted value)
    confidence_intervals = [
        {"low": p * 0.95, "high": p * 1.05} for p in preds
    ]

    response = {
        "symbol": symbol,
        "past_dates": df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        "past_prices": prices.tolist(),
        "future_dates": [
            (df['Date'].iloc[-1] + pd.Timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(1, 8)
        ],
        "predicted_prices": preds,
        "confidence_intervals": confidence_intervals,
        "hour_prediction": preds[0],  # Use the first prediction for the next hour
        "day_prediction": preds[1],  # Use the second prediction for the next day
        "week_prediction": preds[-1],  # Use the last prediction for the next week
    }

    logging.debug("Prediction Response: %s", response)
    return response