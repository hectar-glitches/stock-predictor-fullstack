import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext();

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const toast = { id, message, type, duration };
    
    setToasts(prev => [...prev, toast]);
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
    
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const success = useCallback((message, duration) => 
    addToast(message, 'success', duration), [addToast]);
  
  const error = useCallback((message, duration) => 
    addToast(message, 'error', duration), [addToast]);
  
  const warning = useCallback((message, duration) => 
    addToast(message, 'warning', duration), [addToast]);
  
  const info = useCallback((message, duration) => 
    addToast(message, 'info', duration), [addToast]);

  return (
    <ToastContext.Provider value={{ 
      toasts, 
      addToast, 
      removeToast, 
      success, 
      error, 
      warning, 
      info 
    }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <Toast 
          key={toast.id} 
          toast={toast} 
          onClose={() => removeToast(toast.id)} 
        />
      ))}
    </div>
  );
}

function Toast({ toast, onClose }) {
  const { message, type } = toast;
  
  const typeStyles = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-black',
    info: 'bg-blue-500 text-white',
  };

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <div className={`
      ${typeStyles[type]} 
      px-4 py-3 rounded-lg shadow-lg 
      flex items-center space-x-3 
      min-w-[300px] max-w-[500px]
      transform transition-all duration-300 ease-in-out
      animate-slide-in
    `}>
      <span className="text-lg">{icons[type]}</span>
      <span className="flex-1">{message}</span>
      <button 
        onClick={onClose}
        className="text-lg hover:opacity-75 transition-opacity"
        aria-label="Close notification"
      >
        ×
      </button>
    </div>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

// Default export for simple Toast usage
export default function SimpleToast({ message, type = 'info', isVisible = true, onClose }) {
  if (!isVisible || !message) return null;

  const typeStyles = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-black',
    info: 'bg-blue-500 text-white',
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div
        className={`
          px-4 py-3 rounded-lg shadow-lg flex items-center space-x-3 min-w-0 max-w-sm
          transform transition-all duration-300 ease-in-out
          ${typeStyles[type] || typeStyles.info}
          ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        `}
      >
        <div className="flex-shrink-0">
          {type === 'success' && '✅'}
          {type === 'error' && '❌'}
          {type === 'warning' && '⚠️'}
          {type === 'info' && 'ℹ️'}
        </div>
        <p className="text-sm font-medium flex-1 min-w-0 truncate">
          {message}
        </p>
        {onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 ml-2 hover:opacity-70 transition-opacity"
            aria-label="Close toast"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
