# backend/app.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
import pandas as pd
from datetime import datetime

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import numpy as np
from models.model_loader import ModelLoader

logging.basicConfig(level=logging.DEBUG)

from model import (
    predict_stock,
    convert_to_native_types,
)
import stock_fetcher

app = FastAPI()
model_loader = ModelLoader()

@app.get("/")
async def root():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Restrict to the frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    symbol: str

@app.get("/indexes")
async def get_indexes():
    """Get market indexes data"""
    try:
        indexes = {"DOW": "^DJI", "S&P500": "^GSPC"}
        result = {}
        
        # Get all index data at once
        data = stock_fetcher.get_stock_data(list(indexes.values()), days=5)
        
        # Process the results
        for name, ticker in indexes.items():
            if ticker in data and not data[ticker].empty and 'Close' in data[ticker].columns:
                result[name] = float(data[ticker]['Close'].iloc[-1])
            else:
                result[name] = None
        
        return result
    except Exception as e:
        logging.error(f"Error fetching index data: {str(e)}")
        return {}  # Return empty dict on error

@app.get("/top-stocks")
async def get_top_stocks():
    """Get top stocks closing prices"""
    try:
        TOP_STOCKS = ["AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","BRK-B","JPM","V"]
        return stock_fetcher.get_latest_prices(TOP_STOCKS)
    except Exception as e:
        logging.error(f"Error fetching top stocks: {str(e)}")
        return {}

@app.get("/stock-stats")
async def stock_stats(symbol: str = Query(...), days: int = Query(1)):
    """Get latest stats for a stock"""
    try:
        # Get stock data from our new fetcher
        data = stock_fetcher.get_stock_data(symbol, days)
        
        if symbol not in data or data[symbol].empty:
            return {
                "last": None,
                "high": None,
                "low": None,
                "volume": None,
                "error": f"No data found for {symbol}."
            }
        
        df = data[symbol]
        # Check if required columns exist
        required_columns = ['Close', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                "last": None,
                "high": None,
                "low": None, 
                "volume": None,
                "error": f"Missing data columns for {symbol}: {', '.join(missing_columns)}"
            }
            
        # Get latest row
        latest = df.iloc[-1]
        
        # Convert all values to native Python types
        return {
            "last": float(latest['Close']) if not pd.isna(latest['Close']) else None,
            "high": float(latest['High']) if not pd.isna(latest['High']) else None,
            "low": float(latest['Low']) if not pd.isna(latest['Low']) else None,
            "volume": int(latest['Volume']) if not pd.isna(latest['Volume']) else None
        }
    except Exception as e:
        logging.error(f"Error in stock_stats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-ohlc")
async def stock_ohlc(symbol: str, days: int = 180):
    """
    Get historical OHLC data for a stock
    """
    logging.info(f"OHLC request for symbol={symbol}, days={days}")
    try:
        # Use the new stock fetcher
        data = stock_fetcher.get_stock_data(symbol, days)
        
        if symbol not in data or data[symbol].empty:
            logging.error(f"No data returned for symbol={symbol}")
            return []
            
        df = data[symbol]
        
        # Ensure we have the required data
        if 'Date' not in df.columns or 'Close' not in df.columns:
            logging.error(f"Missing required columns in data for {symbol}")
            return []
        
        # Convert to the expected format
        result = []
        for _, row in df.iterrows():
            # Format the date as string
            date_str = row['Date'].strftime('%Y-%m-%d') if isinstance(row['Date'], (datetime, pd.Timestamp)) else str(row['Date'])
            
            # Add the data point
            result.append({
                'date': date_str,
                'close': float(row['Close'])
            })
            
        return result
    except Exception as e:
        logging.error(f"Error in stock_ohlc endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/predict")
async def predict_stock(request: PredictRequest):
    try:
        symbol = request.symbol  # Extract the symbol from the request body
        # Each predictions with a different time period
        predictions = {
            "next_hour": await calculate_prediction(symbol, period="1h"),
            "next_day": await calculate_prediction(symbol, period="1d"),
            "next_week": await calculate_prediction(symbol, period="1w")
        }
        logging.debug("Predictions Response: %s", predictions)  # Log the predictions
        return predictions
    except Exception as e:
        logging.error("Error in /predict endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def calculate_prediction(symbol: str, period: str):
    """Calculate stock price prediction for a given symbol and period."""
    try:
        # Load historical data for the stock
        df = get_history(symbol, days=180)

        # Check if DataFrame is empty using .empty property
        if df.empty or 'Close' not in df.columns:
            logging.warning(f"Insufficient or invalid historical data for {symbol}. Cannot predict for {period}.")
            return {
                "value": None,
                "confidence_interval": {"low": None, "high": None},
                "error": f"Insufficient historical data for {symbol} to make a prediction for {period}."
            }
        
        # Check if all values in Close column are NaN using .all() method
        if df['Close'].isnull().all():
            logging.warning(f"All Close values are NaN for {symbol}. Cannot predict for {period}.")
            return {
                "value": None,
                "confidence_interval": {"low": None, "high": None},
                "error": f"All price data is missing for {symbol} for {period}."
            }

        # Drop NaNs from prices before using
        prices = df['Close'].dropna().values
        
        # Check if the resulting array is empty after removing NaNs
        if len(prices) == 0:
            logging.warning(f"No valid price data for {symbol} after cleaning. Cannot predict for {period}.")
            return {
                "value": None,
                "confidence_interval": {"low": None, "high": None},
                "error": f"No valid price data for {symbol} for {period}."
            }
            
        X = np.arange(len(prices)).reshape(-1, 1)

        # Load the appropriate model for the time period
        model_name = f"{symbol}_{period}_model"
        model = model_loader.load_model(model_name) # This can raise FileNotFoundError

        # Generate predictions for the next time period
        if period == "1h":
            future_X = np.array([len(prices)]).reshape(-1, 1)
        elif period == "1d":
            future_X = np.array([len(prices) + 1]).reshape(-1, 1)
        elif period == "1w":
            future_X = np.array([len(prices) + 7]).reshape(-1, 1)
        else:
            # Handle unexpected periods gracefully
            # or handled by a default prediction/error.
            logging.error(f"Invalid period: {period} for symbol {symbol}")
            raise ValueError(f"Invalid period: {period}") # Or return an error structure

        prediction_result = model.predict(future_X)
        logging.debug(f"Raw prediction result for {symbol} {period}: {prediction_result}")

        # === Add check for prediction result before indexing ===
        if prediction_result is None or len(prediction_result) == 0:
            logging.error(f"Model prediction returned empty or invalid result for {symbol}, period {period}.")
            return {
                "value": None,
                "confidence_interval": {"low": None, "high": None},
                "error": f"Model prediction failed for {symbol} {period}."
            }
        # =====================================================

        prediction = prediction_result[0]

        # Add confidence intervals
        confidence_interval = {
            "low": prediction * 0.95,
            "high": prediction * 1.05
        }

        return {
            "value": prediction,
            "confidence_interval": confidence_interval
        }
    except FileNotFoundError:
        logging.warning(f"Model file not found for {symbol} and {period}.")
        # Return specific structure indicating model not found
        # This allows the main /predict endpoint to still return other successful predictions
        return {
            "value": None,
            "confidence_interval": {"low": None, "high": None},
            "error": f"Prediction model not available for {symbol} {period}."
        }
    except ValueError as ve: # Catch specific errors like invalid period
        logging.error(f"Value error during prediction for {symbol} {period}: {str(ve)}")
        # Depending on how you want to handle this, you might return an error structure
        # or re-raise as an HTTPException if it's a client-side error.
        # For now, let's return an error structure to be consistent.
        return {
            "value": None,
            "confidence_interval": {"low": None, "high": None},
            "error": f"Invalid input for prediction: {str(ve)}"
        }
    except Exception as e:
        # Log the full traceback for unexpected errors
        logging.exception(f"Unexpected error calculating prediction for {symbol} and {period}: {str(e)}")
        # Return a generic error structure
        return {
            "value": None,
            "confidence_interval": {"low": None, "high": None},
            "error": f"Internal error during prediction for {symbol} {period}."
        }

@app.get("/compare")
async def compare(symbol1: str = Query(...), symbol2: str = Query(...)):
    """Compare predictions for two stocks"""
    try:
        # Use a helper function to ensure all values are JSON serializable
        return {
            symbol1: convert_to_native_types(predict_stock(symbol1)),
            symbol2: convert_to_native_types(predict_stock(symbol2)),
        }
    except Exception as e:
        logging.error(f"Error in compare endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))