"""Production-ready FastAPI application for stock prediction."""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional
import os

# Local imports
from config import settings
from logging_config import configure_logging, get_logger
from middleware import MonitoringMiddleware, SecurityMiddleware, limiter, metrics_endpoint
from models.model_loader import ModelLoader
from model import predict_stock, convert_to_native_types
import stock_fetcher

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting up application")
    
    # Startup
    try:
        # Initialize model loader
        global model_loader
        model_loader = ModelLoader()
        logger.info("Model loader initialized")
        
        # Pre-load commonly used models if needed
        # model_loader.load_model("AAPL", "1d")  # Example
        
        yield
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e), exc_info=True)
        raise
    finally:
        # Shutdown
        logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="Stock Predictor API",
    description="A production-ready API for stock price prediction and analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Security
security = HTTPBearer(auto_error=False)

# Add middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(MonitoringMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter


# Pydantic models
class PredictRequest(BaseModel):
    symbol: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class StockStatsResponse(BaseModel):
    last: Optional[float]
    high: Optional[float]
    low: Optional[float]
    volume: Optional[int]
    error: Optional[str] = None


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "ok", "message": "Stock Predictor API"}


# Rate-limited endpoints
@app.get("/indexes")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_indexes(request):
    """Get market indexes data."""
    try:
        logger.info("Fetching market indexes")
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
                logger.warning("No data found for index", index=name, ticker=ticker)
        
        logger.info("Successfully fetched market indexes", result=result)
        return result
        
    except Exception as e:
        logger.error("Error fetching index data", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch market data")


@app.get("/top-stocks")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_top_stocks(request):
    """Get top stocks closing prices."""
    try:
        logger.info("Fetching top stocks")
        TOP_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JPM", "V"]
        result = stock_fetcher.get_latest_prices(TOP_STOCKS)
        logger.info("Successfully fetched top stocks", count=len(result))
        return result
        
    except Exception as e:
        logger.error("Error fetching top stocks", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch stock data")


@app.get("/stock-stats", response_model=StockStatsResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def stock_stats(request, symbol: str = Query(..., description="Stock symbol"), 
                     days: int = Query(1, ge=1, le=365, description="Number of days")):
    """Get latest stats for a stock."""
    try:
        logger.info("Fetching stock stats", symbol=symbol, days=days)
        
        # Validate symbol
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid stock symbol")
        
        # Get stock data
        data = stock_fetcher.get_stock_data(symbol.upper(), days)
        
        if symbol.upper() not in data or data[symbol.upper()].empty:
            logger.warning("No data found for symbol", symbol=symbol)
            return StockStatsResponse(
                last=None, high=None, low=None, volume=None,
                error=f"No data found for {symbol}."
            )

        df = data[symbol.upper()]
        
        # Check if required columns exist
        required_columns = ['Close', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning("Missing data columns", symbol=symbol, missing=missing_columns)
            return StockStatsResponse(
                last=None, high=None, low=None, volume=None,
                error=f"Missing data columns for {symbol}: {', '.join(missing_columns)}"
            )

        # Calculate stats
        stats = StockStatsResponse(
            last=float(df['Close'].iloc[-1]),
            high=float(df['High'].max()),
            low=float(df['Low'].min()),
            volume=int(df['Volume'].sum())
        )
        
        logger.info("Successfully fetched stock stats", symbol=symbol, stats=stats.dict())
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching stock stats", symbol=symbol, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch stock statistics")


@app.get("/stock-data")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_stock_data(request, symbol: str = Query(...), days: int = Query(30)):
    """Get historical stock data."""
    try:
        logger.info("Fetching stock data", symbol=symbol, days=days)
        
        # Validate inputs
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid stock symbol")
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
        
        data = stock_fetcher.get_stock_data(symbol.upper(), days)
        
        if symbol.upper() not in data or data[symbol.upper()].empty:
            logger.warning("No data found for symbol", symbol=symbol)
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        df = data[symbol.upper()]
        
        # Convert to JSON-serializable format
        result = {
            "symbol": symbol.upper(),
            "data": df.reset_index().to_dict('records')
        }
        
        # Convert numpy types to native Python types
        result = convert_to_native_types(result)
        
        logger.info("Successfully fetched stock data", symbol=symbol, records=len(result["data"]))
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching stock data", symbol=symbol, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch stock data")


@app.post("/predict")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def predict_endpoint(request, predict_request: PredictRequest):
    """Predict stock prices."""
    try:
        symbol = predict_request.symbol.upper()
        logger.info("Making prediction", symbol=symbol)
        
        # Validate symbol
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid stock symbol")
        
        predictions = predict_stock(symbol, model_loader)
        
        if not predictions:
            logger.warning("No predictions generated", symbol=symbol)
            raise HTTPException(status_code=404, detail=f"Could not generate predictions for {symbol}")
        
        result = convert_to_native_types(predictions)
        logger.info("Successfully generated predictions", symbol=symbol)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error making prediction", symbol=symbol, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate predictions")


# Metrics endpoint for monitoring
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return await metrics_endpoint()


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.warning("HTTP exception", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Initialize global variables
model_loader = None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
