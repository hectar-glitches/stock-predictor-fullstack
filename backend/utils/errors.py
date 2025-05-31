from fastapi import HTTPException
from typing import Dict, Any

class StockAPIError(HTTPException):
    def __init__(self, detail: str, code: str = None):
        super().__init__(status_code=400, detail={"message": detail, "code": code})

class RateLimitError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail={"message": "Too many requests. Please try again later.", "code": "RATE_LIMIT_EXCEEDED"}
        )

def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format error response for consistent error handling"""
    if isinstance(error, HTTPException):
        return {"error": error.detail}
    return {
        "error": {
            "message": str(error),
            "code": error.__class__.__name__
        }
    }
