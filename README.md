# Stock Predictor Fullstack Application

A production-ready fullstack application for predicting stock prices and analyzing market sentiment.

## 🚀 Features

- **Stock Price Display**: View historical price data for various stocks
- **Price Predictions**: ML-based predictions for 1 hour, 1 day, and 1 week timeframes
- **Market Sentiment Analysis**: Uses Alpha Vantage API to analyze sentiment for stocks
- **Real-time Data**: Fetches latest stock data from Yahoo Finance API
- **Production Ready**: Docker support, monitoring, logging, and security features

## 🛠 Technology Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **ML Model**: LightGBM for stock price prediction
- **Data Sources**: Yahoo Finance API for stock data, Alpha Vantage API for sentiment
- **Database**: PostgreSQL (production) / SQLite (development)
- **Caching**: Redis
- **Monitoring**: Prometheus metrics
- **Deployment**: Docker + Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

## 🚀 Quick Start (Production)

1. **Clone the repository**:
```bash
git clone https://github.com/hectar-glitches/stock-predictor-fullstack.git
cd stock-predictor-fullstack
```

2. **Configure environment**:
```bash
# Copy and edit the environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and configuration
```

3. **Deploy with Docker**:
```bash
./deploy.sh
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## 🔧 Development Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. Run the development server:
```bash
uvicorn app:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## 🐳 Docker Commands

### Build and run all services:
```bash
docker-compose up --build
```

### Run in background:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f [service-name]
```

### Stop all services:
```bash
docker-compose down
```

### Rebuild specific service:
```bash
docker-compose build [service-name]
```

## 📊 API Endpoints

### Health Check
- `GET /health` - Application health status

### Stock Data
- `GET /top-stocks` - Get top 10 stocks data
- `GET /stock-stats?symbol={SYMBOL}&days={DAYS}` - Get stock statistics
- `GET /stock-data?symbol={SYMBOL}&days={DAYS}` - Get historical stock data
- `GET /indexes` - Get market indexes (DOW, S&P 500)

### Predictions
- `POST /predict` - Generate stock price predictions

### Monitoring
- `GET /metrics` - Prometheus metrics

## 🔐 Environment Variables

### Backend (.env)
```bash
# API Keys
ALPHA_VANTAGE_API_KEY=your_key_here

# Model Configuration
MODEL_N_ESTIMATORS=100
MODEL_LEARNING_RATE=0.05
MODEL_MAX_DEPTH=5

# Cache Configuration
CACHE_TTL_MINUTES=15
STOCK_CACHE_SIZE=100

# Logging
LOG_LEVEL=INFO

# Server Configuration
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Database (for production)
DATABASE_URL=postgresql://user:password@db:5432/stockpredictor

# Security
SECRET_KEY=your-secret-key-here
RATE_LIMIT_PER_MINUTE=60

# Environment
ENVIRONMENT=production
```

## 📈 Monitoring & Observability

### Metrics
The application exposes Prometheus metrics at `/metrics` endpoint:
- HTTP request counts and durations
- Error rates
- Custom business metrics

### Logging
Structured logging with configurable levels:
- JSON format in production
- Console format in development
- Request/response logging
- Error tracking

### Health Checks
- Application health endpoint: `/health`
- Docker health checks configured
- Database connectivity checks

## 🔒 Security Features

- Rate limiting on all endpoints
- CORS configuration
- Security headers (HSTS, XSS protection, etc.)
- Input validation and sanitization
- Error handling without information leakage
- Non-root Docker containers

## 🚀 Production Deployment

### Using Docker Compose (Recommended)
1. Configure production environment variables
2. Run `./deploy.sh` for automated deployment
3. Set up reverse proxy (Nginx configuration included)
4. Configure SSL certificates
5. Set up monitoring and alerting

### Manual Deployment
1. Build Docker images
2. Deploy to container orchestration platform (Kubernetes, ECS, etc.)
3. Configure load balancer
4. Set up database and Redis instances
5. Configure monitoring and logging

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 API Documentation

When running in development mode, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000, 8000, 5432, and 6379 are available
2. **API key errors**: Ensure Alpha Vantage API key is properly configured
3. **Docker issues**: Restart Docker daemon and try again
4. **Memory issues**: Increase Docker memory allocation for large datasets

### Logs
Check application logs for detailed error information:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📞 Support

For support and questions, please open an issue in the GitHub repository.
```
npm run dev
```

4. Access the application at `http://localhost:5173`

## API Keys

- **Alpha Vantage API**: For sentiment analysis, get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and update it in `frontend/src/App.jsx`

## Troubleshooting

### Chart Not Displaying

If the chart is not displaying, ensure:
1. The backend `/stock-ohlc` endpoint is returning data
2. The data has `date` and `close` fields (lowercase)
3. CORS is properly configured for the frontend origin

### Sentiment Analysis Not Working

If sentiment analysis is not displaying:
1. Check you have a valid Alpha Vantage API key and you're hiding it when you publish.
2. Check the browser console for API error messages
3. Note that Alpha Vantage has rate limits for free accounts (typically 5 calls per minute)
