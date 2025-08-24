"""Configuration management for the application."""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    alpha_vantage_api_key: Optional[str] = None
    
    # Model Configuration
    model_n_estimators: int = 100
    model_learning_rate: float = 0.05
    model_max_depth: int = 5
    
    # Cache Configuration
    cache_ttl_minutes: int = 15
    stock_cache_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    database_url: str = "sqlite:///./stock_predictor.db"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    rate_limit_per_minute: int = 60
    
    # Redis (for production caching)
    redis_url: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator('debug', mode='before')
    @classmethod
    def get_debug(cls, v, info):
        if info.data.get('environment') == 'production':
            return False
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
