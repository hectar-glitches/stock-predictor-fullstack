/**
 * API Configuration and utilities
 */

// Environment variables with fallbacks
export const config = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  ALPHA_VANTAGE_API_KEY: import.meta.env.VITE_ALPHA_VANTAGE_API_KEY || 'demo',
  NODE_ENV: import.meta.env.VITE_NODE_ENV || 'development',
  IS_PRODUCTION: import.meta.env.VITE_NODE_ENV === 'production'
};

// API endpoints
export const endpoints = {
  STOCK_STATS: (symbol) => `${config.API_URL}/stock-stats?symbol=${symbol}`,
  STOCK_DATA: (symbol, days = 30) => `${config.API_URL}/stock-data?symbol=${symbol}&days=${days}`,
  PREDICT: `${config.API_URL}/predict`,
  TOP_STOCKS: `${config.API_URL}/top-stocks`,
  INDEXES: `${config.API_URL}/indexes`,
  HEALTH: `${config.API_URL}/health`
};

// Alpha Vantage API
export const alphaVantageEndpoint = (symbol) => 
  `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=${symbol}&apikey=${config.ALPHA_VANTAGE_API_KEY}`;

/**
 * Enhanced fetch with error handling and timeout
 */
export const apiFetch = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    
    throw error;
  }
};

/**
 * Logger utility (only logs in development)
 */
export const logger = {
  log: (...args) => {
    if (!config.IS_PRODUCTION) {
      console.log(...args);
    }
  },
  error: (...args) => {
    if (!config.IS_PRODUCTION) {
      console.error(...args);
    }
  },
  warn: (...args) => {
    if (!config.IS_PRODUCTION) {
      console.warn(...args);
    }
  }
};
