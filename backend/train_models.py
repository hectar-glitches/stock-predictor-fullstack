import os
import joblib
import numpy as np
from model import get_history
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def train_and_save_model(symbol: str, period: str):
    """Train and save a model for a specific stock and time period."""
    df = get_history(symbol, days=180)
    prices = df['Close'].values
    X = np.arange(len(prices)).reshape(-1, 1)

    # Define the target variable based on the period
    if period == "1h":
        y = prices  # Use the same prices for hourly prediction
    elif period == "1d":
        y = np.roll(prices, -1)[:-1]  # Shift prices by 1 day
        X = X[:-1]  # Remove the last day
    elif period == "1w":
        y = np.roll(prices, -7)[:-7]  # Shift prices by 7 days
        X = X[:-7]  # Remove the last 7 days
    else:
        raise ValueError(f"Invalid period: {period}")

    # Normalize the features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = LGBMRegressor()
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error for {symbol} ({period}): {mse}")

    # Save the model
    models_dir = os.path.join(os.path.dirname(__file__), "models", "trained_models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f"{symbol}_{period}_model.joblib")
    joblib.dump(model, model_path)
    print(f"Model saved: {model_path}")

# train models for all stocks and periods
if __name__ == "__main__":
    symbols = ['AAPL','MSFT','GOOGL','AMZN','TSLA',
  'NVDA','META','BRK-B','JPM','V','IBM']
    periods = ["1h", "1d", "1w"]

    for symbol in symbols:
        for period in periods:
            train_and_save_model(symbol, period)