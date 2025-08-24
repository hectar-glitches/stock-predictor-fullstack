import React from 'react';

// Simple Error component with default export
function Error({ 
  message, 
  onRetry, 
  title = 'Error',
  className = '' 
}) {
  return (
    <div className={`bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-6 ${className}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <span className="text-2xl">❌</span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
            {title}
          </h3>
          {message && (
            <p className="text-red-700 dark:text-red-300 mb-4">
              {message}
            </p>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors duration-200"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default Error;
