# Stock Predictor Fullstack Application

A fullstack application for predicting stock prices and analyzing market sentiment.

## Features

- **Stock Price Display**: View historical price data for various stocks
- **Price Predictions**: ML-based predictions for 1 hour, 1 day, and 1 week timeframes
- **Market Sentiment Analysis**: Uses Alpha Vantage API to analyze sentiment for stocks
- **Real-time Data**: Fetches latest stock data from Yahoo Finance API

## Technology Stack

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI (Python)
- **ML Model**: LightGBM for stock price prediction
- **Data Sources**: Yahoo Finance API for stock data, Alpha Vantage API for sentiment

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```
cd backend
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the server:
```
uvicorn app:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```
cd frontend
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm run dev
```

4. Access the application at `http://localhost:5173`

## API Keys

- **Alpha Vantage API**: For sentiment analysis, get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and update it in `frontend/src/App.jsx`

## Troubleshooting

### Chart Not Displaying

If the chart is not displaying, ensure:
1. The backend `/stock-ohlc` endpoint is returning data
2. The data has `date` and `close` fields (lowercase)
3. CORS is properly configured for the frontend origin

### Sentiment Analysis Not Working

If sentiment analysis is not displaying:
1. Check you have a valid Alpha Vantage API key and you're hiding it when you publish.
2. Check the browser console for API error messages
3. Note that Alpha Vantage has rate limits for free accounts (typically 5 calls per minute)
