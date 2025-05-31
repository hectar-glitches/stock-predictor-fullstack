import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_stock_stats():
    response = client.get("/stock-stats?symbol=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert "last" in data
    assert "high" in data
    assert "low" in data
    assert "volume" in data

def test_invalid_symbol():
    response = client.get("/stock-stats?symbol=INVALID")
    assert response.status_code == 200
    data = response.json()
    assert data["error"] is not None

def test_ohlc_data():
    response = client.get("/stock-ohlc?symbol=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "date" in data[0]
        assert "close" in data[0]
