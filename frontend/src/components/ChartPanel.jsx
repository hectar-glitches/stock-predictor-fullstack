import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';

export default function ChartPanel({ ohlc, loading }) {
  console.log('OHLC Data:', ohlc); // Debugging the data

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  if (!ohlc || ohlc.length === 0) {
    return <div className="flex justify-center items-center h-64">No data available</div>;
  }

  // Format data for the chart
  const chartData = ohlc
    .filter(item => item.Date && item.Close) // Use 'Date' and 'Close' fields
    .map(item => ({
      date: new Date(item.Date).toLocaleDateString(), // Use item.Date
      close: parseFloat(item.Close) // Use item.Close
    }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis domain={['auto', 'auto']} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#22c55e"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}