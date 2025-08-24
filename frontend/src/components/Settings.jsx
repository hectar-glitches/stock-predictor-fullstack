import React, { useState } from 'react';
import { useStock } from '../context/StockContext';
import { useTheme } from '../hooks';

export default function Settings({ isOpen, onClose }) {
  const { state, actions } = useStock();
  const { theme, toggleTheme } = useTheme();
  const [tempSettings, setTempSettings] = useState({
    autoRefresh: state.autoRefresh,
    refreshInterval: state.refreshInterval / 1000 / 60, // Convert to minutes
    theme: theme,
  });

  const handleSave = () => {
    actions.setAutoRefresh(tempSettings.autoRefresh);
    // Convert minutes back to milliseconds
    actions.setRefreshInterval(tempSettings.refreshInterval * 60 * 1000);
    
    if (tempSettings.theme !== theme) {
      actions.setTheme(tempSettings.theme);
    }
    
    onClose();
  };

  const handleReset = () => {
    setTempSettings({
      autoRefresh: false,
      refreshInterval: 5,
      theme: 'light',
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">
            Settings
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label="Close settings"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Theme Setting */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Theme
            </label>
            <select
              value={tempSettings.theme}
              onChange={(e) => setTempSettings(prev => ({ ...prev, theme: e.target.value }))}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>

          {/* Auto Refresh Setting */}
          <div>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={tempSettings.autoRefresh}
                onChange={(e) => setTempSettings(prev => ({ ...prev, autoRefresh: e.target.checked }))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Auto-refresh data
              </span>
            </label>
          </div>

          {/* Refresh Interval Setting */}
          {tempSettings.autoRefresh && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Refresh Interval (minutes)
              </label>
              <input
                type="number"
                min="1"
                max="60"
                value={tempSettings.refreshInterval}
                onChange={(e) => setTempSettings(prev => ({ 
                  ...prev, 
                  refreshInterval: Math.max(1, parseInt(e.target.value) || 1)
                }))}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200"
              />
            </div>
          )}

          {/* Data Management */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Management
            </label>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
              className="w-full p-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
            >
              Clear All Data & Reset
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3 mt-6">
          <button
            onClick={handleReset}
            className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Reset
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
