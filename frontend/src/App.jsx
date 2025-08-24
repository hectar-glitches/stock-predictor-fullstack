import React, { useState, useEffect } from 'react';
import './index.css';
import { StockProvider, useStock } from './context/StockContext';
import { useTheme, useToast } from './hooks';
import Navbar from './components/Navbar.jsx';
import Sidebar from './components/Sidebar.jsx';
import PredictionsPanel from './components/PredictionsPanel.jsx';
import ChartPanel from './components/ChartPanel.jsx';
import SummaryStats from './components/SummaryStats.jsx';
import Settings from './components/Settings.jsx';
import Toast from './components/Toast.jsx';
import Loading from './components/Loading.jsx';
import Error from './components/ErrorSimple.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';

function AppContent() {
  const { state, actions } = useStock();
  const { theme } = useTheme();
  const { toast, showToast } = useToast();
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  useEffect(() => {
    // Initial data fetch
    if (!state.stockData || !state.predictions) {
      handleFetchData();
    }
  }, [state.selectedSymbol, state.timeframe]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!state.autoRefresh) return;

    const interval = setInterval(() => {
      handleFetchData(true); // Silent refresh
    }, state.refreshInterval);

    return () => clearInterval(interval);
  }, [state.autoRefresh, state.refreshInterval, state.selectedSymbol, state.timeframe]);

  const handleFetchData = async (silent = false) => {
    try {
      await actions.fetchStockData(state.selectedSymbol, state.timeframe);
      await actions.fetchPredictions(state.selectedSymbol, state.timeframe);
      
      if (silent) {
        showToast('Data refreshed', 'success');
      }
    } catch (error) {
      showToast(error.message || 'Failed to fetch data', 'error');
    }
  };

  const handleStockSelect = (stock) => {
    actions.setSymbol(stock);
    showToast(`Selected ${stock}`, 'info');
  };

  const handleTimeframeSelect = (timeframe) => {
    actions.setTimeframe(timeframe);
    showToast(`Timeframe changed to ${timeframe}`, 'info');
  };

  const handleRetry = () => {
    actions.clearError();
    handleFetchData();
  };

  if (state.loading && !state.stockData) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <Loading.Spinner size="large" />
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      theme === 'dark' 
        ? 'bg-gray-900 text-gray-100' 
        : 'bg-gray-100 text-gray-900'
    }`}>
      <Navbar 
        onRefresh={() => handleFetchData()}
        onSettingsClick={() => setShowSettings(true)}
        loading={state.loading}
        autoRefresh={state.autoRefresh}
      />
      
      <div className="flex">
        <Sidebar 
          selectedStock={state.selectedSymbol}
          timeframe={state.timeframe}
          onStockSelect={handleStockSelect}
          onTimeframeSelect={handleTimeframeSelect}
          loading={state.loading}
        />
        
        <main className="flex-1 p-6">
          {state.error && (
            <Error 
              message={state.error}
              onRetry={handleRetry}
              className="mb-6"
            />
          )}
          
          {state.stockData && (
            <>
              <SummaryStats 
                stockData={state.stockData}
                loading={state.loading}
              />
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                <ChartPanel 
                  stockData={state.stockData}
                  loading={state.loading}
                />
                <PredictionsPanel 
                  predictions={state.predictions} 
                  currentPrice={state.stockData?.current_price}
                  symbol={state.selectedSymbol}
                  loading={state.loading}
                />
              </div>
            </>
          )}

          {!state.stockData && !state.loading && !state.error && (
            <div className="flex flex-col items-center justify-center h-64">
              <p className="text-gray-500 dark:text-gray-400 text-lg mb-4">
                Select a stock to get started
              </p>
              <button
                onClick={() => handleFetchData()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
              >
                Load Data
              </button>
            </div>
          )}
        </main>
      </div>

      {/* Settings Modal */}
      <Settings 
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />

      {/* Toast Notifications */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={() => showToast('', 'info', false)}
      />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <StockProvider>
        <AppContent />
      </StockProvider>
    </ErrorBoundary>
  );
}

export default App;
