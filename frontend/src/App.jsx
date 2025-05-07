import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import SummaryStats from './components/SummaryStats';
import ChartPanel from './components/ChartPanel';
import PredictionsPanel from './components/PredictionsPanel';
import ErrorBoundary from './components/ErrorBoundary';

async function fetchSentiment(symbol) {
  const apiKey = 'VALID_API_KEY';
  const url = `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=${symbol}&apikey=${apiKey}`;

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Failed to fetch sentiment data: ${response.status}`);
    const data = await response.json();

     // Debugging log

    console.log('Sentiment API Response:', data);

    // Handle rate limit or invalid inputs
    if (data.Information || data.Note) {
      return { sentimentScore: null, sentimentLabel: 'Rate limit exceeded or invalid API key' };
    }

    // Handle missing or empty feed
    if (!data.feed || data.feed.length === 0) {
      return { sentimentScore: null, sentimentLabel: 'No sentiment data available' };
    }

    // Parse sentiment data from the response
    const sentimentScore = data.feed[0].overall_sentiment_score;
    const sentimentLabel = data.feed[0].overall_sentiment_label;
    return { sentimentScore, sentimentLabel };
  } catch (err) {
    console.error('Error fetching sentiment data:', err); // Debugging log
    return { sentimentScore: null, sentimentLabel: 'Error fetching sentiment data' };
  }
}

export default function App() {
  const [symbol, setSymbol] = useState('AAPL'); // Default stock symbol
  const [sentiment, setSentiment] = useState({ sentimentScore: null, sentimentLabel: '' });
  const [stockStats, setStockStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [autoFetch, setAutoFetch] = useState(false); // Flag to control auto-fetching
  const [ohlcData, setOhlcData] = useState([]);
  const [predictions, setPredictions] = useState(null);

  // Function to handle symbol change
  const onChangeSymbol = (newSymbol) => {
    setSymbol(newSymbol); // Update the selected stock symbol
    setAutoFetch(false); // Disable auto-fetching after user interaction
  };

  // Function to fetch sentiment data
  const fetchSentimentData = async (currentSymbol) => {
    setLoading(true);
    const result = await fetchSentiment(currentSymbol);
    setSentiment(result);
    setLoading(false);
  };

  // Function to fetch stock data (OHLC, predictions, and stats)
  const fetchStockData = async (currentSymbol) => {
    setLoading(true);
    try {
      // Fetch OHLC data
      const ohlcResponse = await fetch(`http://localhost:8000/stock-ohlc?symbol=${currentSymbol}`);
      if (!ohlcResponse.ok) throw new Error(`Failed to fetch OHLC data: ${ohlcResponse.status}`);
      const ohlcData = await ohlcResponse.json();
      console.log('OHLC API Response:', ohlcData); 
      setOhlcData(ohlcData);

      // Fetch predictions
      const predResponse = await fetch(`http://localhost:8000/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: currentSymbol }),
      });
      if (!predResponse.ok) throw new Error(`Failed to fetch predictions: ${predResponse.status}`);
      const predData = await predResponse.json();
      setPredictions(predData);

      // Fetch Stock Stats <-- Add this fetch
      const statsResponse = await fetch(`http://localhost:8000/stock-stats?symbol=${currentSymbol}`);
      if (!statsResponse.ok) throw new Error(`Failed to fetch stock stats: ${statsResponse.status}`);
      const statsData = await statsResponse.json();
      setStockStats(statsData); // <-- Set the stats state

    } catch (err) {
      console.error('Error fetching stock data:', err);
      setOhlcData([]); 
      setPredictions(null);
      setStockStats({}); // <-- Clear stats on error
    } finally {
      setLoading(false);
    }
  };

  // Fetch data when autoFetch is true or symbol changes
  useEffect(() => {
    if (autoFetch && symbol) {
      Promise.all([
        fetchSentimentData(symbol),
        fetchStockData(symbol) // This now fetches stats too
      ]);
      setAutoFetch(false); 
    }
  }, [autoFetch, symbol]);

  return (
    <ErrorBoundary>
      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar
          symbol={symbol}
          onChangeSymbol={onChangeSymbol} 
          onUpdate={() => {
            setAutoFetch(true); 
          }}
          loading={loading}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          <Navbar />
          <div className="flex-1 flex flex-col lg:flex-row gap-6 p-6 bg-gray-100 dark:bg-gray-800 overflow-auto">
            {/* Left Panel */}
            <div className="w-full lg:w-1/3 flex flex-col gap-6">
              <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-6">
                {/* Pass stockStats to SummaryStats */}
                <SummaryStats stats={stockStats} loading={loading} /> 
              </div>
              <div className={`p-6 rounded-lg shadow-lg ${
                sentiment.sentimentLabel === 'Positive'
                  ? 'bg-green-100 dark:bg-green-900'
                  : sentiment.sentimentLabel === 'Negative'
                  ? 'bg-red-100 dark:bg-red-900'
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-200">
                  Current Sentiment
                </h3>
                <div className="flex items-center space-x-4 mb-4">
                  <span className="text-4xl">
                    {sentiment.sentimentLabel === 'Positive' ? '📈' :
                     sentiment.sentimentLabel === 'Negative' ? '📉' :
                     sentiment.sentimentLabel === 'Neutral' ? '⚖️' : '❓'}
                  </span>
                  <p className={`text-lg font-semibold ${
                    sentiment.sentimentLabel === 'Positive'
                      ? 'text-green-700 dark:text-green-300'
                      : sentiment.sentimentLabel === 'Negative'
                      ? 'text-red-700 dark:text-red-300'
                      : 'text-gray-700 dark:text-gray-300'
                  }`}>
                    {loading
                      ? 'Loading sentiment analysis...'
                      : sentiment.sentimentLabel
                      ? `${sentiment.sentimentLabel} (Score: ${
                          sentiment.sentimentScore !== null
                            ? sentiment.sentimentScore.toFixed(2)
                            : 'N/A'
                        })`
                      : 'No sentiment data available'}
                  </p>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {loading
                    ? 'Fetching sentiment data...'
                    : sentiment.sentimentLabel === 'Rate limit exceeded or invalid API key'
                    ? 'API rate limit exceeded or invalid API key. Please try again later.'
                    : sentiment.sentimentLabel === 'Error fetching sentiment data'
                    ? 'Unable to fetch sentiment data. Please check your connection or API key.'
                    : sentiment.sentimentLabel
                    ? `${sentiment.sentimentLabel} (Score: ${
                        sentiment.sentimentScore !== null
                          ? sentiment.sentimentScore.toFixed(2)
                          : 'N/A'
                      })`
                    : 'No sentiment data available.'}
                </p>
              </div>
            </div>

            {/* Right Panel */}
            <div className="w-full lg:w-2/3 flex flex-col gap-6">
              <div className="flex-1 bg-white dark:bg-gray-700 rounded-lg shadow-lg p-6">
                <ChartPanel ohlc={ohlcData} loading={loading} />
              </div>
              <div className="flex-1 bg-white dark:bg-gray-700 rounded-lg shadow-lg p-6">
                <PredictionsPanel predictions={predictions} loading={loading} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}