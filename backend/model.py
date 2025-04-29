# backend/model.py
import yfinance as yf
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
import logging
logging.basicConfig(level=logging.DEBUG)


model = LGBMRegressor()
trained = False

def get_history(symbol, days=180):
    df = yf.download(symbol, period=f"{days}d")[['Open','High','Low','Close','Volume']].dropna()
    df['Date'] = df.index
    return df.reset_index(drop=True)

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
    df = get_history(symbol, days)[['Date', 'Open', 'High', 'Low', 'Close']]
    logging.debug("Before date conversion:\n%s", df.head())  # Debugging log

    # Flatten column names if they are multi-indexed
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    # Convert Date to datetime and remove timezone information
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.tz_localize(None)

    if df['Date'].isnull().any():
        logging.error("Date conversion failed for some rows. Dropping invalid rows.")
        df = df.dropna(subset=['Date'])  # Drop rows with invalid dates

    # Create the 'time' column
    df['time'] = df['Date'].dt.strftime('%Y-%m-%d')

    # Rename columns and return as a list of dictionaries
    result = df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'
    })[['time', 'open', 'high', 'low', 'close']].to_dict(orient='records')

    logging.debug("OHLC result:\n%s", result)  # Log the result
    return result

def predict_stock(symbol):
    global trained, model
    df = get_history(symbol, days=180)
    prices = df['Close'].values
    X = np.arange(len(prices)).reshape(-1,1)
    if not trained:
        model.fit(X, prices)
        trained = True
    future_X = np.arange(len(prices), len(prices)+7).reshape(-1,1)
    preds = model.predict(future_X).tolist()
    response = {
        "symbol": symbol,
        "past_dates": df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        "past_prices": prices.tolist(),
        "future_dates": [
            (df['Date'].iloc[-1] + pd.Timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(1,8)
        ],
        "predicted_prices": preds,
    }
    
    logging.debug(response)
    return response