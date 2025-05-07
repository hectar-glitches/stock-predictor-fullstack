import React, { useState, useEffect } from 'react';

export default function Navbar() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    // toggle the 'dark' class on the root element
    document.documentElement.classList.toggle('dark', dark);
  }, [dark]);

  return (
    <header className="bg-gradient-to-r from-blue-500 to-indigo-500 dark:from-gray-800 dark:to-gray-900 shadow-lg p-4 mb-6 transition-all sticky top-0 z-10">
      <div className="flex justify-between items-center max-w-6xl mx-auto">
        {/* title */}
        <h1 className="text-2xl font-extrabold text-white tracking-wide">
          📈 Stock Market Dashboard
        </h1>

        {/* dark Mode Toggle */}
        <button
          onClick={() => setDark(!dark)}
          className="p-2 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full shadow-md hover:shadow-lg transition-all"
        >
          {dark ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
    </header>
  );
}