import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { apiFetch, endpoints, logger } from '../config/api';

// Initial state
const initialState = {
  // Current selection
  selectedSymbol: 'AAPL',
  
  // Data states
  stockData: null,
  stockStats: {},
  predictions: null,
  sentiment: { sentimentScore: null, sentimentLabel: '' },
  topStocks: [],
  indexes: {},
  
  // UI states
  loading: {
    stockData: false,
    predictions: false,
    sentiment: false,
    topStocks: false,
    indexes: false,
  },
  
  // Error states
  errors: {
    stockData: null,
    predictions: null,
    sentiment: null,
    topStocks: null,
    indexes: null,
  },
  
  // Settings
  autoRefresh: false,
  refreshInterval: 300000, // 5 minutes
  theme: 'light',
};

// Action types
const actionTypes = {
  SET_SYMBOL: 'SET_SYMBOL',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_STOCK_DATA: 'SET_STOCK_DATA',
  SET_STOCK_STATS: 'SET_STOCK_STATS',
  SET_PREDICTIONS: 'SET_PREDICTIONS',
  SET_SENTIMENT: 'SET_SENTIMENT',
  SET_TOP_STOCKS: 'SET_TOP_STOCKS',
  SET_INDEXES: 'SET_INDEXES',
  SET_AUTO_REFRESH: 'SET_AUTO_REFRESH',
  SET_THEME: 'SET_THEME',
  CLEAR_ERRORS: 'CLEAR_ERRORS',
};

// Reducer
function stockReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_SYMBOL:
      return {
        ...state,
        selectedSymbol: action.payload,
        // Clear data when symbol changes
        stockData: null,
        stockStats: {},
        predictions: null,
        sentiment: { sentimentScore: null, sentimentLabel: '' },
      };
      
    case actionTypes.SET_LOADING:
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.value,
        },
      };
      
    case actionTypes.SET_ERROR:
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.payload.key]: action.payload.value,
        },
        loading: {
          ...state.loading,
          [action.payload.key]: false,
        },
      };
      
    case actionTypes.SET_STOCK_DATA:
      return {
        ...state,
        stockData: action.payload,
        errors: { ...state.errors, stockData: null },
        loading: { ...state.loading, stockData: false },
      };
      
    case actionTypes.SET_STOCK_STATS:
      return {
        ...state,
        stockStats: action.payload,
        errors: { ...state.errors, stockStats: null },
        loading: { ...state.loading, stockStats: false },
      };
      
    case actionTypes.SET_PREDICTIONS:
      return {
        ...state,
        predictions: action.payload,
        errors: { ...state.errors, predictions: null },
        loading: { ...state.loading, predictions: false },
      };
      
    case actionTypes.SET_SENTIMENT:
      return {
        ...state,
        sentiment: action.payload,
        errors: { ...state.errors, sentiment: null },
        loading: { ...state.loading, sentiment: false },
      };
      
    case actionTypes.SET_TOP_STOCKS:
      return {
        ...state,
        topStocks: action.payload,
        errors: { ...state.errors, topStocks: null },
        loading: { ...state.loading, topStocks: false },
      };
      
    case actionTypes.SET_INDEXES:
      return {
        ...state,
        indexes: action.payload,
        errors: { ...state.errors, indexes: null },
        loading: { ...state.loading, indexes: false },
      };
      
    case actionTypes.SET_AUTO_REFRESH:
      return {
        ...state,
        autoRefresh: action.payload,
      };
      
    case actionTypes.SET_THEME:
      return {
        ...state,
        theme: action.payload,
      };
      
    case actionTypes.CLEAR_ERRORS:
      return {
        ...state,
        errors: initialState.errors,
      };
      
    default:
      return state;
  }
}

// Create context
const StockContext = createContext();

// Provider component
export function StockProvider({ children }) {
  const [state, dispatch] = useReducer(stockReducer, initialState);

  // Actions
  const actions = {
    setSymbol: (symbol) => {
      dispatch({ type: actionTypes.SET_SYMBOL, payload: symbol });
      // Save to localStorage
      localStorage.setItem('selectedSymbol', symbol);
    },
    
    setLoading: (key, value) => {
      dispatch({ type: actionTypes.SET_LOADING, payload: { key, value } });
    },
    
    setError: (key, error) => {
      dispatch({ type: actionTypes.SET_ERROR, payload: { key, value: error } });
      logger.error(`Error in ${key}:`, error);
    },
    
    fetchStockData: async (symbol) => {
      actions.setLoading('stockData', true);
      try {
        const data = await apiFetch(endpoints.STOCK_DATA(symbol, 30));
        dispatch({ type: actionTypes.SET_STOCK_DATA, payload: data });
      } catch (error) {
        actions.setError('stockData', error.message);
      }
    },
    
    fetchStockStats: async (symbol) => {
      actions.setLoading('stockStats', true);
      try {
        const data = await apiFetch(endpoints.STOCK_STATS(symbol));
        dispatch({ type: actionTypes.SET_STOCK_STATS, payload: data });
      } catch (error) {
        actions.setError('stockStats', error.message);
      }
    },
    
    fetchPredictions: async (symbol) => {
      actions.setLoading('predictions', true);
      try {
        const data = await apiFetch(endpoints.PREDICT, {
          method: 'POST',
          body: JSON.stringify({ symbol }),
        });
        dispatch({ type: actionTypes.SET_PREDICTIONS, payload: data });
      } catch (error) {
        actions.setError('predictions', error.message);
      }
    },
    
    fetchTopStocks: async () => {
      actions.setLoading('topStocks', true);
      try {
        const data = await apiFetch(endpoints.TOP_STOCKS);
        dispatch({ type: actionTypes.SET_TOP_STOCKS, payload: data });
      } catch (error) {
        actions.setError('topStocks', error.message);
      }
    },
    
    fetchIndexes: async () => {
      actions.setLoading('indexes', true);
      try {
        const data = await apiFetch(endpoints.INDEXES);
        dispatch({ type: actionTypes.SET_INDEXES, payload: data });
      } catch (error) {
        actions.setError('indexes', error.message);
      }
    },
    
    setTheme: (theme) => {
      dispatch({ type: actionTypes.SET_THEME, payload: theme });
      localStorage.setItem('theme', theme);
      document.documentElement.className = theme;
    },
    
    clearErrors: () => {
      dispatch({ type: actionTypes.CLEAR_ERRORS });
    },
  };

  // Load saved preferences on mount
  useEffect(() => {
    const savedSymbol = localStorage.getItem('selectedSymbol');
    const savedTheme = localStorage.getItem('theme');
    
    if (savedSymbol) {
      dispatch({ type: actionTypes.SET_SYMBOL, payload: savedSymbol });
    }
    
    if (savedTheme) {
      actions.setTheme(savedTheme);
    }
  }, []);

  // Auto-refresh functionality
  useEffect(() => {
    if (!state.autoRefresh) return;

    const interval = setInterval(() => {
      if (state.selectedSymbol) {
        actions.fetchStockData(state.selectedSymbol);
        actions.fetchStockStats(state.selectedSymbol);
        actions.fetchTopStocks();
        actions.fetchIndexes();
      }
    }, state.refreshInterval);

    return () => clearInterval(interval);
  }, [state.autoRefresh, state.selectedSymbol, state.refreshInterval]);

  return (
    <StockContext.Provider value={{ state, actions }}>
      {children}
    </StockContext.Provider>
  );
}

// Custom hook
export function useStock() {
  const context = useContext(StockContext);
  if (!context) {
    throw new Error('useStock must be used within a StockProvider');
  }
  return context;
}
