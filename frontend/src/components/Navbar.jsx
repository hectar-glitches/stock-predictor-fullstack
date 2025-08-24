import React from 'react';
import { useTheme } from '../hooks';

export default function Navbar({ onRefresh, onSettingsClick, loading, autoRefresh }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-gradient-to-r from-blue-500 to-indigo-500 dark:from-gray-800 dark:to-gray-900 shadow-lg p-4 mb-6 transition-all sticky top-0 z-10">
      <div className="flex justify-between items-center max-w-6xl mx-auto">
        {/* Title */}
        <h1 className="text-2xl font-extrabold text-white tracking-wide">
          📈 Stock Market Dashboard
        </h1>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          {/* Auto-refresh indicator */}
          {autoRefresh && (
            <div className="flex items-center text-white text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
              Auto-refresh
            </div>
          )}

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 bg-white/20 hover:bg-white/30 disabled:bg-white/10 text-white rounded-full shadow-md hover:shadow-lg transition-all disabled:cursor-not-allowed"
            title="Refresh data"
          >
            <svg 
              className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
              />
            </svg>
          </button>

          {/* Settings Button */}
          <button
            onClick={onSettingsClick}
            className="p-2 bg-white/20 hover:bg-white/30 text-white rounded-full shadow-md hover:shadow-lg transition-all"
            title="Settings"
          >
            <svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" 
              />
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
              />
            </svg>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full shadow-md hover:shadow-lg transition-all"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </header>
  );
}