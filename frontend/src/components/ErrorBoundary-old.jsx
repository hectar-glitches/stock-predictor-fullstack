import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return import React from 'react';
import { FallbackError } from './Error';
import { logger } from '../config/api';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    this.setState({ errorInfo });
    
    // Log to console in development
    logger.error('Error caught by ErrorBoundary:', error);
    logger.error('Error Info:', errorInfo);
    
    // You could also log to an error reporting service here
    // errorReportingService.captureException(error, { extra: errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleReset);
      }
      
      // Default fallback UI
      return (
        <FallbackError 
          error={this.state.error} 
          resetError={this.handleReset} 
        />
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;