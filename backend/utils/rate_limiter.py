from functools import wraps
import time
from collections import deque
import logging

class RateLimiter:
    def __init__(self, max_calls, time_window):
        """
        Initialize a rate limiter that allows max_calls within time_window seconds.
        
        Args:
            max_calls (int): Maximum number of calls allowed
            time_window (float): Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        logging.debug(f"Initialized RateLimiter with max_calls={max_calls}, time_window={time_window}s")
        
    def limit(self, func):
        """
        Decorator method to limit the rate of function calls.
        
        Args:
            func: The function to be rate limited
            
        Returns:
            wrapped: The wrapped function with rate limiting
        """
        return self.__call__(func)
        
    def __call__(self, func):
        """
        Alternative way to use the rate limiter as a decorator.
        
        Args:
            func: The function to be rate limited
            
        Returns:
            wrapped: The wrapped function with rate limiting
        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the time window
            while self.calls and now - self.calls[0] >= self.time_window:
                self.calls.popleft()
                
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    logging.warning(f"Rate limit reached for {func.__name__}. Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
            
            try:
                self.calls.append(now)
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logging.error(f"Error in rate-limited function {func.__name__}: {str(e)}")
                raise
                
        return wrapped
