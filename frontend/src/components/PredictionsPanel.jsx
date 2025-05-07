import React from 'react';

export default function PredictionsPanel({ predictions, loading }) {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <p className="text-lg font-semibold">Loading predictions…</p>
      </div>
    );
  }

  if (!predictions) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <p className="text-lg font-semibold">No predictions available</p>
        <p className="text-sm">Click "Update" to load predictions</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {Object.entries(predictions).map(([period, data]) => {
        const value = data?.value ?? 'N/A';
        const low = data?.confidence_interval?.low ?? 'N/A';
        const high = data?.confidence_interval?.high ?? 'N/A';

        return (
          <div key={period} className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold">
              {period.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </h3>
            <p className="text-xl font-bold">
              ${typeof value === 'number' ? value.toFixed(2) : value}
            </p>
            <p className="text-sm text-gray-500">
              Confidence Interval: ${typeof low === 'number' ? low.toFixed(2) : low} - ${typeof high === 'number' ? high.toFixed(2) : high}
            </p>
          </div>
        );
      })}
    </div>
  );
}