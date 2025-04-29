import React from 'react';

export default function SummaryStats({ stats, loading }) {
  const items = [
    ['Last Price', stats?.last],
    ['High',       stats?.high],
    ['Low',        stats?.low],
    ['Volume',     stats?.volume],
  ];

  if (loading && !stats) {
    return <div className="text-center py-20 text-gray-500">Loading stats…</div>;
  }

  if (!stats) {
    return <div className="text-center py-20 text-gray-400">Click “Update” to load data</div>;
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {items.map(([label, value]) => (
        <div
          key={label}
          className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow h-24 flex flex-col justify-center"
        >
          <p className="text-sm text-gray-500 dark:text-gray-300">{label}</p>
          <p className="text-xl font-bold">{value?.toLocaleString() ?? '--'}</p>
        </div>
      ))}
    </div>
  );
}