# backend/app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import logging  # Import logging

logging.basicConfig(level=logging.DEBUG)  # Configure logging

from model import (
    predict_stock,
    fetch_top_stocks,
    fetch_index_data,
    fetch_stock_stats,
    get_ohlc,               
)

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    result = get_ohlc(symbol, days)
    logging.debug("Response for /stock-ohlc:\n%s", result)
    return jsonable_encoder(result)

@app.post("/predict")
async def predict(req: PredictRequest):
    return predict_stock(req.symbol)

@app.get("/compare")
async def compare(symbol1: str = Query(...), symbol2: str = Query(...)):
    return {
        symbol1: predict_stock(symbol1),
        symbol2: predict_stock(symbol2),
    }