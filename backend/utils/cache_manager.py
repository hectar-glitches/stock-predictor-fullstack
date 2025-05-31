"""Cache management utilities for the stock predictor application."""
from pathlib import Path
import json
import time
import logging
import pandas as pd

class CacheManager:
    def __init__(self, cache_dir: str, ttl_config: dict):
        """Initialize cache manager with directory and TTL configuration."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_config = ttl_config

    def get_cache_path(self, key: str, type_: str = "history", days: int = 180) -> Path:
        """Generate a cache file path for the given parameters."""
        return self.cache_dir / f"{key}_{type_}_{days}.json"

    def is_valid(self, cache_path: Path, ttl: int) -> bool:
        """Check if cache file exists and is not expired."""
        if not cache_path.exists():
            return False
        file_age = time.time() - cache_path.stat().st_mtime
        return file_age < ttl

    def save(self, data, cache_path: Path) -> None:
        """Save data to cache file."""
        try:
            cache_data = {
                "timestamp": time.time(),
                "data": self._prepare_data_for_cache(data)
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            logging.debug(f"Saved data to cache: {cache_path}")
        except Exception as e:
            logging.warning(f"Failed to save to cache: {e}")

    def load(self, cache_path: Path):
        """Load data from cache file."""
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            return self._restore_data_from_cache(cache_data.get("data"))
        except Exception as e:
            logging.warning(f"Failed to load from cache: {e}")
            return None

    def _prepare_data_for_cache(self, data):
        """Convert data to JSON-serializable format."""
        if isinstance(data, dict):
            return {k: self._prepare_data_for_cache(v) for k, v in data.items()}
        elif isinstance(data, pd.DataFrame):
            return data.to_dict(orient="split")
        return data

    def _restore_data_from_cache(self, data):
        """Restore data from cached format."""
        if isinstance(data, dict):
            if all(k in data for k in ["index", "columns", "data"]):
                return pd.DataFrame(**data)
            return {k: self._restore_data_from_cache(v) for k, v in data.items()}
        return data

    def clear_expired(self) -> None:
        """Remove all expired cache entries."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                # Determine TTL based on filename
                if "latest" in cache_file.name:
                    ttl = self.ttl_config["latest"]
                else:
                    ttl = self.ttl_config["history"]
                
                if not self.is_valid(cache_file, ttl):
                    cache_file.unlink()
                    logging.info(f"Removed expired cache file: {cache_file}")
            except Exception as e:
                logging.error(f"Error cleaning cache file {cache_file}: {e}")

    def clear_all(self) -> None:
        """Remove all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logging.error(f"Error removing cache file {cache_file}: {e}")
        logging.info("Cache cleared")
