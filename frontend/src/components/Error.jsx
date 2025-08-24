import React from 'react';

export function ErrorCard({ 
  title = 'Error', 
  message, 
  onRetry, 
  retryText = 'Try Again',
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
              {retryText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function ErrorMessage({ message, className = '' }) {
  return (
    <div className={`text-red-600 dark:text-red-400 text-sm ${className}`}>
      ⚠️ {message}
    </div>
  );
}

export function NetworkErrorCard({ onRetry }) {
  return (
    <ErrorCard
      title="Network Error"
      message="Unable to connect to the server. Please check your internet connection and try again."
      onRetry={onRetry}
      retryText="Retry Connection"
    />
  );
}

export function NotFoundCard({ item = 'Data', onRetry }) {
  return (
    <ErrorCard
      title={`${item} Not Found`}
      message={`The requested ${item.toLowerCase()} could not be found.`}
      onRetry={onRetry}
      retryText="Go Back"
    />
  );
}

export function FallbackError({ error, resetError }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full">
        <ErrorCard
          title="Something went wrong"
          message={
            error?.message || 
            'An unexpected error occurred. Please refresh the page or try again later.'
          }
          onRetry={resetError}
          retryText="Reset Application"
        />
      </div>
    </div>
  );
}

// Default export - main Error component
export default function Error({ 
  message, 
  onRetry, 
  title = 'Error',
  className = '',
  type = 'card' 
}) {
  switch (type) {
    case 'message':
      return <ErrorMessage message={message} className={className} />;
    case 'network':
      return <NetworkErrorCard onRetry={onRetry} />;
    case 'notfound':
      return <NotFoundCard onRetry={onRetry} />;
    case 'fallback':
      return <FallbackError error={{ message }} resetError={onRetry} />;
    default:
      return (
        <ErrorCard
          title={title}
          message={message}
          onRetry={onRetry}
          className={className}
        />
      );
  }
}
