import React from 'react';

export function LoadingSpinner({ size = 'md', color = 'blue' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  };

  const colorClasses = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    red: 'border-red-500',
    gray: 'border-gray-500',
  };

  return (
    <div 
      className={`
        ${sizeClasses[size]} 
        ${colorClasses[color]}
        border-2 border-t-transparent 
        rounded-full animate-spin
      `}
      role="status"
      aria-label="Loading"
    />
  );
}

export function LoadingCard({ title = 'Loading...', description, className = '' }) {
  return (
    <div className={`bg-white dark:bg-gray-700 rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center space-x-4">
        <LoadingSpinner size="md" />
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export function LoadingOverlay({ message = 'Loading...', transparent = false }) {
  return (
    <div className={`
      fixed inset-0 z-50 flex items-center justify-center
      ${transparent ? 'bg-black bg-opacity-50' : 'bg-white dark:bg-gray-900'}
    `}>
      <div className="text-center">
        <LoadingSpinner size="xl" />
        <p className="mt-4 text-lg font-medium text-gray-700 dark:text-gray-300">
          {message}
        </p>
      </div>
    </div>
  );
}

export function SkeletonLoader({ className = '', rows = 3 }) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="mb-3">
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-4/5"></div>
        </div>
      ))}
    </div>
  );
}

// Legacy Spinner component for backward compatibility
function Spinner({ className = '', size = 'medium' }) {
  return (
    <div className={`flex justify-center items-center ${className}`}>
      <LoadingSpinner size={size} />
    </div>
  );
}

// Export all loading components as an object
const Loading = {
  Spinner,
  Card: LoadingCard,
  Overlay: LoadingOverlay,
  Skeleton: SkeletonLoader
};

export default Loading;
