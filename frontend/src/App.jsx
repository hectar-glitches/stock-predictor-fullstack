import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import SummaryStats from './components/SummaryStats';
import ChartPanel from './components/ChartPanel';

export default function App() {
  const [symbol, setSymbol]   = useState('AAPL');
  const [stats, setStats]     = useState(null);
  const [ohlc, setOhlc]       = useState(null);
  const [loading, setLoading] = useState(false);

  // Only run when user clicks "Update"
  const handleUpdate = async () => {
    setLoading(true);
    try {
      const [statRes, ohlcRes] = await Promise.all([
        fetch(`http://127.0.0.1:8002/stock-stats?symbol=${symbol}`),
        fetch(`http://127.0.0.1:8002/stock-ohlc?symbol=${symbol}&days=90`)
      ]);

      if (!statRes.ok || !ohlcRes.ok) {
        throw new Error(`Stats: ${statRes.status}, OHLC: ${ohlcRes.status}`);
      }

      const statJson = await statRes.json();
      const ohlcJson = await ohlcRes.json();
      setStats(statJson);
      setOhlc(ohlcJson);
    } catch (err) {
      console.error(err);
      alert('Error loading data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar
        symbol={symbol}
        onChangeSymbol={setSymbol}
        onUpdate={handleUpdate}
        loading={loading}
      />

      <div className="flex-1 flex flex-col bg-slate-50 dark:bg-gray-800">
        <Navbar />

        <div className="flex-1 p-6 overflow-auto flex flex-col lg:flex-row gap-6">
          <div className="w-full lg:w-1/3">
            <SummaryStats stats={stats} loading={loading} />
          </div>
          <div className="w-full lg:w-2/3">
            <ChartPanel ohlc={ohlc} loading={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}