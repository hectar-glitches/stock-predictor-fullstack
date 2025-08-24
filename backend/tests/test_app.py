import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_indexes():
    response = client.get("/indexes")
    assert response.status_code == 200
    data = response.json()
    # Should return a dict, even if empty on error
    assert isinstance(data, dict)

def test_stock_stats():
    response = client.get("/stock-stats?symbol=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert "last" in data or "error" in data

def test_invalid_symbol():
    response = client.get("/stock-stats?symbol=INVALID12345")
    assert response.status_code == 200
    data = response.json()
    # Should either have data or an error message
    assert "error" in data or "last" in data
    assert isinstance(data, list)
    if len(data) > 0:
        assert "date" in data[0]
        assert "close" in data[0]
