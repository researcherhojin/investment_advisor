"""
Data Module

Handles all data fetching and processing for stock analysis.
"""

from .base import StockDataFetcher
from .stable_fetcher import StableFetcher
from .simple_fetcher import SimpleStockFetcher

__all__ = [
    'StockDataFetcher',
    'StableFetcher', 
    'SimpleStockFetcher',
]