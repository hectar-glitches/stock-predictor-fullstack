import React, { useRef, useEffect } from 'react';
import { createChart } from 'lightweight-charts';

export default function ChartPanel({ ohlc, loading }) {
  const ref = useRef();

  useEffect(() => {
    if (!ohlc) return;
    const chart = createChart(ref.current, {
      width: ref.current.clientWidth,
      height: 300,
      layout: {
        backgroundColor: '#ffffff',
        textColor: '#333333'
      },
      grid: {
        vertLines: { color: '#eee' },
        horzLines: { color: '#eee' }
      }
    });

    const series = chart.addCandlestickSeries({
      upColor: '#10b981', downColor: '#ef4444',
      borderUpColor: '#10b981', borderDownColor: '#ef4444',
      wickUpColor: '#10b981', wickDownColor: '#ef4444'
    });
    series.setData(ohlc);

    const resize = () => chart.resize(ref.current.clientWidth, 300);
    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
      chart.remove();
    };
  }, [ohlc]);

  if (loading && !ohlc) {
    return <div className="text-center py-20 text-gray-500">Loading chart…</div>;
  }

  if (!ohlc) {
    return <div className="text-center py-20 text-gray-400">Click “Update” to load chart</div>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <div ref={ref} className="w-full h-80" />
    </div>
  );
}