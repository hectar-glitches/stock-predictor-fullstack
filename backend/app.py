# backend/app.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import numpy as np
from model import get_history
from models.model_loader import ModelLoader
import logging

logging.basicConfig(level=logging.DEBUG)  # Configure logging

from model import (
    predict_stock,
    fetch_top_stocks,
    fetch_index_data,
    fetch_stock_stats,
    get_ohlc,
)

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
    return fetch_index_data()

@app.get("/top-stocks")
async def get_top_stocks():
    return fetch_top_stocks()

@app.get("/stock-stats")
async def stock_stats(symbol: str = Query(...), days: int = Query(1)):
    return fetch_stock_stats(symbol, days)

@app.get("/stock-ohlc")
async def stock_ohlc(symbol: str = Query(...), days: int = Query(180)):
    logging.debug("Received /stock-ohlc request with symbol=%s, days=%d", symbol, days)
    result = get_ohlc(symbol, days) 
    logging.debug("Response for /stock-ohlc:\n%s", result)
    return jsonable_encoder(result)

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
        prices = df['Close'].values
        X = np.arange(len(prices)).reshape(-1, 1)

        # Load the appropriate model for the time period
        model_name = f"{symbol}_{period}_model"
        model = model_loader.load_model(model_name)

        # Generate predictions for the next time period
        if period == "1h":
            future_X = np.array([len(prices)]).reshape(-1, 1)  # Predict the next hour
        elif period == "1d":
            future_X = np.array([len(prices) + 1]).reshape(-1, 1)  # Predict the next day
        elif period == "1w":
            future_X = np.array([len(prices) + 7]).reshape(-1, 1)  # Predict the next week
        else:
            raise ValueError(f"Invalid period: {period}")

        prediction = model.predict(future_X)[0]

        # Add confidence intervals (e.g., ±5% of the predicted value)
        confidence_interval = {
            "low": prediction * 0.95,
            "high": prediction * 1.05
        }

        return {
            "value": prediction,
            "confidence_interval": confidence_interval
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Model for {symbol} and {period} not found.")
    except Exception as e:
        logging.error(f"Error calculating prediction for {symbol} and {period}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compare")
async def compare(symbol1: str = Query(...), symbol2: str = Query(...)):
    return {
        symbol1: predict_stock(symbol1),
        symbol2: predict_stock(symbol2),
    }