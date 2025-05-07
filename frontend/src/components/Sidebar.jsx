import React from 'react';

const STOCK_OPTIONS = [
  'AAPL','MSFT','GOOGL','AMZN','TSLA',
  'NVDA','META','BRK-B','JPM','V','IBM'
];

export default function Sidebar({ symbol, onChangeSymbol, onUpdate, loading }) {
  return (
    <aside className="w-72 bg-gray-900 text-gray-100 p-6 flex flex-col shadow-lg">
      <h2 className="text-lg font-semibold mb-4">⚙️ Stock Options</h2>

      <label htmlFor="ticker" className="text-sm mb-1">Pick a stock</label>
      <select
        id="ticker"
        value={symbol}
        onChange={e => onChangeSymbol(e.target.value)}
        className="w-full mb-4 p-2 rounded bg-gray-800 text-white focus:ring-2 focus:ring-blue-500"
      >
        {STOCK_OPTIONS.map(t => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>

      <button
        onClick={onUpdate}
        disabled={loading}
        className="py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded text-white font-semibold transition"
      >
        {loading ? 'Loading…' : 'Update'}
      </button>
    </aside>
  );
}