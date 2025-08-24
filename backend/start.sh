#!/bin/bash

# Production startup script for the backend
# This script is used in the Docker container

set -e

echo "🚀 Starting Stock Predictor API..."

# Check if running in production
if [[ "${ENVIRONMENT}" == "production" ]]; then
    echo "📊 Running in PRODUCTION mode"
    # Use Gunicorn with multiple workers in production
    exec gunicorn app_production:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers ${WORKERS:-4} \
        --bind 0.0.0.0:${PORT:-8000} \
        --timeout 120 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile -
else
    echo "🔧 Running in DEVELOPMENT mode"
    # Use Uvicorn with hot reload in development
    exec uvicorn app:app \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --reload \
        --log-level debug
fi
