import React from 'react';

export default function SummaryStats({ stats, loading }) {
  if (loading) {
    return <p className="text-gray-500">Loading stats...</p>;
  }

  // Use the keys returned by /stock-stats endpoint
  const { last, high, low, volume } = stats || {}; 

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <h4 className="text-sm font-semibold text-gray-500">Last Price</h4>
        <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
          {last !== undefined ? `$${last.toFixed(2)}` : '--'} {/* Use 'last' */}
        </p>
      </div>
      <div>
        <h4 className="text-sm font-semibold text-gray-500">High</h4>
        <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
          {high !== undefined ? `$${high.toFixed(2)}` : '--'}
        </p>
      </div>
      <div>
        <h4 className="text-sm font-semibold text-gray-500">Low</h4>
        <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
          {low !== undefined ? `$${low.toFixed(2)}` : '--'}
        </p>
      </div>
      <div>
        <h4 className="text-sm font-semibold text-gray-500">Volume</h4>
        <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
          {volume !== undefined ? volume.toLocaleString() : '--'}
        </p>
      </div>
    </div>
  );
}
