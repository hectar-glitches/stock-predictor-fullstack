import { useState, useEffect, useCallback } from 'react';
import { alphaVantageEndpoint, apiFetch, logger } from '../config/api';

/**
 * Hook for fetching Alpha Vantage sentiment data
 */
export function useSentiment() {
  const [sentiment, setSentiment] = useState({
    sentimentScore: null,
    sentimentLabel: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSentiment = useCallback(async (symbol) => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const url = alphaVantageEndpoint(symbol);
      const data = await apiFetch(url);
      
      logger.log('Sentiment API Response:', data);

      // Handle rate limit or invalid inputs
      if (data.Information || data.Note) {
        setSentiment({
          sentimentScore: null,
          sentimentLabel: 'Rate limit exceeded or invalid API key'
        });
        return;
      }

      // Handle missing or empty feed
      if (!data.feed || data.feed.length === 0) {
        setSentiment({
          sentimentScore: null,
          sentimentLabel: 'No sentiment data available'
        });
        return;
      }

      // Parse sentiment data from the response
      const sentimentScore = data.feed[0].overall_sentiment_score;
      const sentimentLabel = data.feed[0].overall_sentiment_label;
      
      setSentiment({ sentimentScore, sentimentLabel });
      
    } catch (err) {
      logger.error('Error fetching sentiment data:', err);
      setError(err.message);
      setSentiment({
        sentimentScore: null,
        sentimentLabel: 'Error fetching sentiment data'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  return { sentiment, loading, error, fetchSentiment };
}

/**
 * Hook for managing local storage
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      logger.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      logger.error('Error saving to localStorage:', error);
    }
  }, [key]);

  return [storedValue, setValue];
}

/**
 * Hook for debouncing values
 */
export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook for managing async operations
 */
export function useAsync(asyncFunction, immediate = true) {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setStatus('pending');
    setData(null);
    setError(null);

    try {
      const response = await asyncFunction(...args);
      setData(response);
      setStatus('success');
      return response;
    } catch (error) {
      setError(error);
      setStatus('error');
      throw error;
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return {
    execute,
    status,
    data,
    error,
    isLoading: status === 'pending',
    isError: status === 'error',
    isSuccess: status === 'success',
  };
}

/**
 * Hook for managing theme
 */
export function useTheme() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  const toggleTheme = useCallback(() => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.className = newTheme;
  }, [theme, setTheme]);

  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  return { theme, toggleTheme, setTheme };
}

/**
 * Hook for managing intervals
 */
export function useInterval(callback, delay) {
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (!isActive || delay === null) return;

    const id = setInterval(callback, delay);
    return () => clearInterval(id);
  }, [callback, delay, isActive]);

  return { isActive, setIsActive };
}

/**
 * Hook for managing toast notifications
 */
export function useToast() {
  const [toast, setToast] = useState({
    message: '',
    type: 'info',
    isVisible: false,
  });

  const showToast = useCallback((message, type = 'info', isVisible = true) => {
    setToast({ message, type, isVisible });
    
    if (isVisible) {
      // Auto-hide after 3 seconds
      setTimeout(() => {
        setToast(prev => ({ ...prev, isVisible: false }));
      }, 3000);
    }
  }, []);

  const hideToast = useCallback(() => {
    setToast(prev => ({ ...prev, isVisible: false }));
  }, []);

  return { toast, showToast, hideToast };
}
