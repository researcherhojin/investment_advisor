"""
Base Data Fetcher

Abstract base class for all data fetchers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import hashlib
from pathlib import Path

import pandas as pd
from ..utils.json_encoder import safe_json_dump, safe_json_dumps

logger = logging.getLogger(__name__)


class DataCache:
    """Simple file-based cache for API responses."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(minutes=15)  # 15-minute cache
    
    def _get_cache_key(self, key_data: str) -> str:
        """Generate cache key from input data."""
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key_data: str) -> Optional[Any]:
        """Get data from cache if available and not expired."""
        cache_key = self._get_cache_key(key_data)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is expired
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < self.cache_duration:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_data['data']
                else:
                    logger.debug(f"Cache expired for key: {cache_key}")
                    cache_file.unlink()  # Delete expired cache
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
        return None
    
    def set(self, key_data: str, value: Any) -> None:
        """Store data in cache."""
        cache_key = self._get_cache_key(key_data)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': value
            }
            
            with open(cache_file, 'w') as f:
                safe_json_dump(cache_data, f)
            
            logger.debug(f"Cache set for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
    
    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")


class StockDataFetcher(ABC):
    """Abstract base class for stock data fetchers."""
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache = DataCache() if use_cache else None
    
    @abstractmethod
    def fetch_price_history(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical price data for a stock.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        pass
    
    @abstractmethod
    def fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch company information and key statistics.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with company information
        """
        pass
    
    @abstractmethod
    def fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch financial statements and metrics.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with financial data
        """
        pass
    
    def get_realtime_price(self, ticker: str) -> Optional[float]:
        """
        Get real-time or latest price for a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Latest price or None if unavailable
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            df = self.fetch_price_history(ticker, start_date, end_date)
            
            if not df.empty:
                return df['Close'].iloc[-1]
            
        except Exception as e:
            logger.error(f"Error fetching real-time price: {e}")
        
        return None
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol exists.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if valid, False otherwise
        """
        try:
            info = self.fetch_company_info(ticker)
            return bool(info)
        except Exception:
            return False